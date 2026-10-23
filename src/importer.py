"""
src/importer.py
Robust CSV Ingestion, Validation, Date Normalization, and Export Engine.
Handles malformed data, encodings, duplicates, and quarantines invalid rows.
"""

import hashlib
import io
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd

from src.models import ReviewRecord, ALL_CATEGORIES
from src.classifier import classify_review_text, compute_sentiment_score

REQUIRED_CORE_FIELDS = ["app_name", "app_identifier", "review_text", "rating"]

COLUMN_ALIASES: Dict[str, List[str]] = {
    "app_name": ["app_name", "appname", "app", "title", "application"],
    "app_identifier": ["app_identifier", "package_name", "packagename", "app_id", "bundle_id", "package"],
    "review_id": ["review_id", "id", "reviewid", "uuid"],
    "review_date": ["review_date", "date", "created_at", "timestamp", "review_created_version"],
    "rating": ["rating", "score", "stars", "star_rating"],
    "review_text": ["review_text", "text", "content", "body", "review", "comment"],
    "review_language": ["review_language", "language", "lang"],
    "source": ["source", "platform", "store"],
    "developer_reply": ["developer_reply", "reply", "dev_reply", "reply_text"],
    "is_synthetic": ["is_synthetic", "synthetic", "demo_data"],
}


class CSVImportResult:
    """Detailed summary of the CSV import process."""
    def __init__(self):
        self.total_rows_read: int = 0
        self.valid_records: List[ReviewRecord] = []
        self.quarantined_rows: List[Dict[str, Any]] = []
        self.duplicate_count: int = 0
        self.encoding_used: str = "utf-8"

    @property
    def valid_count(self) -> int:
        return len(self.valid_records)

    @property
    def quarantine_count(self) -> int:
        return len(self.quarantined_rows)


class ReviewImporter:
    """Engine for parsing, validating, and cleaning app review datasets."""

    @staticmethod
    def read_csv_resilient(file_or_path: Union[str, io.BytesIO, io.StringIO]) -> Tuple[pd.DataFrame, str]:
        """Attempts reading CSV using multiple encodings (utf-8, utf-8-sig, latin-1, cp1252)."""
        encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
        
        # If it's BytesIO, get raw bytes so we can try multiple decoders
        if isinstance(file_or_path, io.BytesIO):
            bytes_data = file_or_path.getvalue()
            for enc in encodings:
                try:
                    df = pd.read_csv(io.BytesIO(bytes_data), encoding=enc)
                    return df, enc
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            raise ValueError("Failed to parse CSV with supported encodings (UTF-8, UTF-8-SIG, Latin-1, CP1252).")
        
        elif isinstance(file_or_path, io.StringIO):
            df = pd.read_csv(file_or_path)
            return df, "utf-8"

        else:
            # File path string
            for enc in encodings:
                try:
                    df = pd.read_csv(file_or_path, encoding=enc)
                    return df, enc
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            raise ValueError(f"Could not decode file at {file_or_path} with any supported encoding.")

    @classmethod
    def map_columns(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Maps varying column headers to the canonical schema names."""
        df = df.copy()
        raw_cols = {str(c).strip().lower(): c for c in df.columns}
        rename_map = {}

        for canonical_name, aliases in COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in raw_cols:
                    rename_map[raw_cols[alias]] = canonical_name
                    break

        df = df.rename(columns=rename_map)
        return df

    @classmethod
    def parse_date_safely(cls, val: Any) -> Optional[date]:
        """Parses arbitrary date formats into a standard datetime.date."""
        if pd.isna(val) or val is None or str(val).strip() == "":
            return date.today()

        try:
            parsed = pd.to_datetime(val)
            return parsed.date()
        except Exception:
            # Fallback regex for common ISO YYYY-MM-DD
            try:
                date_str = str(val)[:10]
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                return None

    @classmethod
    def parse_rating_safely(cls, val: Any) -> Optional[int]:
        """Converts rating to integer in [1, 5] range."""
        if pd.isna(val) or val is None:
            return None
        try:
            r = float(val)
            r_int = int(round(r))
            if 1 <= r_int <= 5:
                return r_int
            return None
        except Exception:
            return None

    @classmethod
    def process_dataframe(
        cls,
        df: pd.DataFrame,
        default_app_name: str = "VR Video Player 360",
        default_app_id: str = "com.vrplayer.vrvideoplayer.videos360.vrvideos.vrapp",
        force_synthetic_flag: Optional[bool] = None,
    ) -> CSVImportResult:
        """
        Validates, deduplicates, categorizes, and converts a DataFrame to ReviewRecord instances.
        """
        result = CSVImportResult()
        df_mapped = cls.map_columns(df)
        result.total_rows_read = len(df_mapped)

        seen_review_ids = set()

        for idx, row in df_mapped.iterrows():
            row_dict = row.to_dict()
            quarantine_reasons = []

            # 1. Text extraction & check
            text = str(row_dict.get("review_text", "")).strip()
            if not text or text.lower() == "nan":
                quarantine_reasons.append("Empty review text")

            # 2. Rating validation
            rating_val = cls.parse_rating_safely(row_dict.get("rating"))
            if rating_val is None:
                quarantine_reasons.append(f"Invalid rating value '{row_dict.get('rating')}' (must be 1-5)")

            # 3. Date validation
            date_val = cls.parse_date_safely(row_dict.get("review_date"))
            if date_val is None:
                quarantine_reasons.append(f"Unparseable date value '{row_dict.get('review_date')}'")

            # 4. App Identifier & Name fallback
            app_name = str(row_dict.get("app_name") or default_app_name).strip()
            app_id = str(row_dict.get("app_identifier") or default_app_id).strip()

            if quarantine_reasons:
                result.quarantined_rows.append({
                    "row_index": idx + 1,
                    "reasons": quarantine_reasons,
                    "raw_data": {k: (None if pd.isna(v) else v) for k, v in row_dict.items()},
                })
                continue

            # 5. Review ID generation / deduplication
            raw_id = row_dict.get("review_id")
            if pd.isna(raw_id) or not str(raw_id).strip():
                # Hash text + date to create deterministic review_id
                hash_base = f"{app_id}_{date_val.isoformat()}_{text[:64]}"
                review_id = f"rev_{hashlib.md5(hash_base.encode('utf-8')).hexdigest()[:12]}"
            else:
                review_id = str(raw_id).strip()

            if review_id in seen_review_ids:
                result.duplicate_count += 1
                continue

            seen_review_ids.add(review_id)

            # 6. Classification & Sentiment
            # If user provided a valid category, check it; otherwise classify
            assigned_cat = row_dict.get("category")
            if assigned_cat not in ALL_CATEGORIES:
                assigned_cat, _ = classify_review_text(text, rating_val)

            user_correction = row_dict.get("user_corrected_category")
            if user_correction not in ALL_CATEGORIES:
                user_correction = None

            sentiment = compute_sentiment_score(text, rating_val)

            # 7. Synthetic Flag
            if force_synthetic_flag is not None:
                is_synth = force_synthetic_flag
            else:
                raw_synth = row_dict.get("is_synthetic", False)
                is_synth = bool(raw_synth) and str(raw_synth).lower() not in ["0", "false", "no"]

            # Construct clean validated record
            try:
                record = ReviewRecord(
                    review_id=review_id,
                    app_name=app_name,
                    app_identifier=app_id,
                    review_date=date_val,
                    rating=rating_val,
                    review_text=text,
                    review_language=str(row_dict.get("review_language") or "en"),
                    source=str(row_dict.get("source") or "csv_import"),
                    developer_reply=str(row_dict.get("developer_reply")) if pd.notna(row_dict.get("developer_reply")) else None,
                    is_synthetic=is_synth,
                    category=assigned_cat,
                    user_corrected_category=user_correction,
                    sentiment_score=sentiment,
                )
                result.valid_records.append(record)
            except Exception as e:
                result.quarantined_rows.append({
                    "row_index": idx + 1,
                    "reasons": [f"Pydantic validation failed: {str(e)}"],
                    "raw_data": {k: (None if pd.isna(v) else v) for k, v in row_dict.items()},
                })

        return result

    @classmethod
    def import_from_csv(
        cls,
        file_or_path: Union[str, io.BytesIO, io.StringIO],
        default_app_name: str = "VR Video Player 360",
        default_app_id: str = "com.vrplayer.vrvideoplayer.videos360.vrvideos.vrapp",
        force_synthetic_flag: Optional[bool] = None,
    ) -> CSVImportResult:
        """Top-level pipeline to read and process any CSV file."""
        df, encoding = cls.read_csv_resilient(file_or_path)
        result = cls.process_dataframe(
            df,
            default_app_name=default_app_name,
            default_app_id=default_app_id,
            force_synthetic_flag=force_synthetic_flag,
        )
        result.encoding_used = encoding
        return result

    @staticmethod
    def export_to_csv(df: pd.DataFrame) -> str:
        """Converts review DataFrame to a clean CSV string adhering to canonical schema."""
        cols = [
            "review_id",
            "app_name",
            "app_identifier",
            "review_date",
            "rating",
            "effective_category",
            "sentiment_score",
            "review_text",
            "source",
            "developer_reply",
            "is_synthetic",
        ]
        available_cols = [c for c in cols if c in df.columns]
        return df[available_cols].to_csv(index=False)
