"""
trending_fetcher.py — يجيب Trending Now فقط كل ساعة
"""
import os, json, logging, subprocess
from datetime import datetime, timezone
from supabase import create_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_KEY']
SERPAPI_KEY  = os.environ['SERPAPI_KEY']
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def serpapi_get(params):
    url = 'https://serpapi.com/search.json'
    query = '&'.join(f'{k}={v}' for k,v in params.items())
    r = subprocess.run(['curl','-s','--max-time','60',f'{url}?{query}'], capture_output=True, text=True)
    return json.loads(r.stdout)

def main():
    log.info('Fetching trending...')
    data = serpapi_get({'engine':'google_trends_trending_now','geo':'SA','api_key':SERPAPI_KEY})
    records = []
    for i, item in enumerate(data.get('trending_searches',[])[:20], start=1):
        records.append({'keyword':item.get('query',''),'rank':i,'geo':'SA','fetched_at':datetime.now(timezone.utc).isoformat()})
    if not records:
        log.info('No trending data')
        return
    supabase.table('trends_trending').delete().neq('id', 0).execute()
    for i in range(0, len(records), 50):
        supabase.table('trends_trending').insert(records[i:i+50]).execute()
    log.info(f'Saved {len(records)} trending')

if __name__ == '__main__':
    main()
