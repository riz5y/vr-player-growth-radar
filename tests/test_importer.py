"""
tests/test_importer.py
Tests CSV parsing, date normalizations, deduplication, and quarantine validation.
"""

import io
import pandas as pd
from src.importer import ReviewImporter


def test_import_valid_csv():
    csv_content = """app_name,app_identifier,review_id,review_date,rating,review_text,review_language,source,developer_reply,is_synthetic
VR Player,com.vrplayer.app,r101,2026-10-15,5,Best VR player smooth playback,en,google_play,,True
VR Player,com.vrplayer.app,r102,2026-10-16,1,Too many pop up ads every minute,en,google_play,,True
"""
    result = ReviewImporter.import_from_csv(io.StringIO(csv_content))
    assert result.valid_count == 2
    assert result.quarantine_count == 0
    assert result.duplicate_count == 0
    assert result.valid_records[0].rating == 5
    assert result.valid_records[1].category == "Advertising and monetization"


def test_import_handles_duplicates():
    csv_content = """review_id,rating,review_text
dup_01,5,Awesome app!
dup_01,5,Awesome app!
dup_02,4,Good app
"""
    result = ReviewImporter.import_from_csv(io.StringIO(csv_content))
    assert result.valid_count == 2
    assert result.duplicate_count == 1


def test_import_quarantines_invalid_rows():
    csv_content = """app_name,app_identifier,review_id,review_date,rating,review_text
VR App,com.test,r1,2026-10-10,99,Invalid rating should fail
VR App,com.test,r2,2026-10-10,4,
VR App,com.test,r3,2026-10-10,1,Valid review with normal rating
"""
    result = ReviewImporter.import_from_csv(io.StringIO(csv_content))
    assert result.valid_count == 1
    assert result.quarantine_count == 2
    assert "Invalid rating" in result.quarantined_rows[0]["reasons"][0]
    assert "Empty review text" in result.quarantined_rows[1]["reasons"][0]


def test_column_alias_mapping():
    csv_content = """packageName,stars,content,date
com.vrplayer.alias,5,Love this media player,2026-09-01
"""
    result = ReviewImporter.import_from_csv(io.StringIO(csv_content))
    assert result.valid_count == 1
    rec = result.valid_records[0]
    assert rec.app_identifier == "com.vrplayer.alias"
    assert rec.rating == 5
    assert rec.review_text == "Love this media player"


def test_csv_export_roundtrip():
    csv_content = """app_name,app_identifier,review_id,review_date,rating,review_text,review_language,source,developer_reply,is_synthetic
VR Player,com.vrplayer.app,r101,2026-10-15,5,Best VR player smooth playback,en,google_play,,True
"""
    result = ReviewImporter.import_from_csv(io.StringIO(csv_content))
    df = pd.DataFrame([r.model_dump() for r in result.valid_records])
    df["effective_category"] = df["category"]
    exported = ReviewImporter.export_to_csv(df)
    assert "r101" in exported
    assert "com.vrplayer.app" in exported
