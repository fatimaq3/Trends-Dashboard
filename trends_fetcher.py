import os, json, time, logging, subprocess
from datetime import datetime, timezone
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_KEY']
SERPAPI_KEY  = os.environ['SERPAPI_KEY']
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

KEYWORD_GROUPS = {
    'geopolitical': ['Iran war', 'Israel Gaza', 'حرب إيران', 'غزة'],
    'economic':     ['Saudi Aramco', 'oil price', 'Vision 2030', 'سعر النفط'],
    'saudi_local':  ['رؤية 2030', 'نيوم', 'السعودية', 'الرياض']
}

def serpapi_get(params):
    url = 'https://serpapi.com/search.json'
    query = '&'.join(f'{k}={v}' for k,v in params.items())
    r = subprocess.run(['curl','-s','--max-time','60',f'{url}?{query}'], capture_output=True, text=True)
    return json.loads(r.stdout)

def fetch_interest(keyword, category):
    try:
        log.info(f'Interest: {keyword}')
        data = serpapi_get({'engine':'google_trends','q':keyword.replace(' ','+'),'geo':'SA','date':'today+3-m','data_type':'TIMESERIES','api_key':SERPAPI_KEY})
        records = []
        for point in data.get('interest_over_time',{}).get('timeline_data',[]):
            for val in point.get('values',[]):
                records.append({'keyword':keyword,'category':category,'date':point['date'][:12].strip(),'interest':int(val.get('extracted_value',0)),'geo':'SA','fetched_at':datetime.now(timezone.utc).isoformat()})
        log.info(f'  {len(records)} points')
        return records
    except Exception as e:
        log.error(f'Error {keyword}: {e}')
        return []

def fetch_related(keyword, category):
    try:
        log.info(f'Related: {keyword}')
        data = serpapi_get({'engine':'google_trends','q':keyword.replace(' ','+'),'geo':'SA','date':'today+3-m','data_type':'RELATED_QUERIES','api_key':SERPAPI_KEY})
        records = []
        for qtype in ['rising','top']:
            for item in data.get('related_queries',{}).get(qtype,[]):
                records.append({'main_keyword':keyword,'related_query':item.get('query',''),'value':int(item.get('extracted_value',0)),'query_type':qtype,'category':category,'fetched_at':datetime.now(timezone.utc).isoformat()})
        log.info(f'  {len(records)} related')
        return records
    except Exception as e:
        log.error(f'Error related {keyword}: {e}')
        return []

def fetch_trending():
    try:
        log.info('Trending...')
        data = serpapi_get({'engine':'google_trends_trending_now','geo':'SA','api_key':SERPAPI_KEY})
        records = []
        for i,item in enumerate(data.get('trending_searches',[])[:20],start=1):
            records.append({'keyword':item.get('query',''),'rank':i,'geo':'SA','fetched_at':datetime.now(timezone.utc).isoformat()})
        log.info(f'  {len(records)} trending')
        return records
    except Exception as e:
        log.error(f'Trending error: {e}')
        return []

def save(table, records):
    if not records:
        log.info(f'No records for {table}')
        return
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    supabase.table(table).delete().gte('fetched_at', today).execute()
    for i in range(0, len(records), 50):
        supabase.table(table).insert(records[i:i+50]).execute()
    log.info(f'Saved {len(records)} to {table}')

def main():
    log.info('Starting...')
    all_interest, all_related = [], []
    for category, keywords in KEYWORD_GROUPS.items():
        for kw in keywords:
            all_interest.extend(fetch_interest(kw, category))
            all_related.extend(fetch_related(kw, category))
            time.sleep(1)
    trending = fetch_trending()
    save('trends_interest', all_interest)
    save('trends_trending', trending)
    save('trends_related', all_related)
    log.info('Done!')

if __name__ == '__main__':
    main()
