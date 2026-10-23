from google_play_scraper import app, reviews, search, Sort
import json

package_name = 'com.vrplayer.vrvideoplayer.videos360.vrvideos.vrapp'

info = app(package_name)
print('Target App Info:')
print(json.dumps({
    'title': info.get('title'),
    'installs': info.get('installs'),
    'developer': info.get('developer'),
    'genre': info.get('genre'),
    'description': info.get('description', '')[:200],
    'ratings': info.get('ratings'),
    'score': info.get('score'),
    'url': info.get('url'),
    'icon': info.get('icon'),
    'screenshots': info.get('screenshots', [])[:4],
}, indent=2))

# Search real competitors
search_terms = ['VR video player 360', 'VR 360 player', 'VR player SBS']
competitors = []
seen = {package_name}

for term in search_terms:
    results = search(term, lang='en', country='us', n_hits=10)
    for r in results:
        app_id = r['appId']
        if app_id not in seen:
            seen.add(app_id)
            competitors.append({
                'title': r['title'],
                'appId': r['appId'],
                'score': r.get('score'),
                'developer': r.get('developer'),
                'icon': r.get('icon'),
                'installs': r.get('installs'),
            })

print(f'\nFound {len(competitors)} real-life direct competitors:')
for c in competitors[:8]:
    print(f"- {c['title']} | ID: {c['appId']} | Rating: {c['score']} | Dev: {c['developer']}")

print("\n--- FETCHING REAL REVIEWS FROM TOP COMPETITORS ---")
comps_to_check = [
    'com.Irusu.IrusuVRCinemaPro',
    'com.xojot.vrplayer',
    'com.creativeinnovations.mea',
    'com.vrplayer.vr360videoplayer'
]

for pkg in comps_to_check:
    try:
        res, _ = reviews(pkg, lang='en', country='us', count=15, sort=Sort.NEWEST)
        print(f"\n--- {pkg} (Total fetched: {len(res)}) ---")
        for r in res[:4]:
            print(f"[{r.get('score')}*] {r.get('content')[:120]}")
    except Exception as e:
        print(f"Error for {pkg}:", e)
