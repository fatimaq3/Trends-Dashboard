import os, json, time, logging, subprocess
from datetime import datetime, timezone
from supabase import create_client, Client
from pytrends.request import TrendReq

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_KEY']
SERPAPI_KEY  = os.environ['SERPAPI_KEY']
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

pytrends = TrendReq(hl='ar', tz=180, timeout=(10,25), retries=2, backoff_factor=1.5)

KEYWORD_GROUPS = {
    "economic": {
        "serpapi": ["oil Saudi", "Red Sea Saudi"],
        "pytrends": ["النفط", "البحر الأحمر"]
    },
    "saudi_local": {
        "serpapi": ["Hafiz Saudi", "Saudi education", "Saudi jobs", "Saudi travel", "Qiyas Saudi", "Noor Saudi"],
        "pytrends": ["حافز", "وزارة التعليم", "وظائف", "رحلات", "قياس", "نور"]
    },
    "technology": {
        "serpapi": ["artificial intelligence Saudi", "AI Saudi"],
        "pytrends": ["ذكاء اصطناعي", "الذكاء الاصطناعي"]
    }
}

def serpapi_get(params):
    url = 'https://serpapi.com/search.json'
    query = '&'.join(f'{k}={v}' for k,v in params.items())
    r = subprocess.run(['curl','-s','--max-time','60',f'{url}?{query}'], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except:
        return {}

def fetch_serpapi_interest(keyword, category):
    try:
        log.info(f'SerpAPI Interest: {keyword}')
        data = serpapi_get({'engine':'google_trends','q':keyword.replace(' ','+'),'geo':'SA','date':'today+3-m','data_type':'TIMESERIES','api_key':SERPAPI_KEY})
        records = []
        for point in data.get('interest_over_time',{}).get('timeline_data',[]):
            for val in point.get('values',[]):
                records.append({'keyword':keyword,'category':category,'date':point['date'][:10].strip(),'interest':int(val.get('extracted_value',0)),'geo':'SA','fetched_at':datetime.now(timezone.utc).isoformat()})
        log.info(f'  {len(records)} points')
        return records
    except Exception as e:
        log.error(f'SerpAPI Error {keyword}: {e}')
        return []

def fetch_serpapi_related(keyword, category):
    try:
        data = serpapi_get({'engine':'google_trends','q':keyword.replace(' ','+'),'geo':'SA','date':'today+3-m','data_type':'RELATED_QUERIES','api_key':SERPAPI_KEY})
        records = []
        for qtype in ['rising','top']:
            for item in data.get('related_queries',{}).get(qtype,[]):
                records.append({'main_keyword':keyword,'related_query':item.get('query',''),'value':int(item.get('extracted_value',0)),'query_type':qtype,'category':category,'fetched_at':datetime.now(timezone.utc).isoformat()})
        return records
    except:
        return []

def fetch_pytrends_interest(keyword, category):
    try:
        log.info(f'Pytrends Interest: {keyword}')
        time.sleep(10)
        pytrends.build_payload([keyword], timeframe='today 3-m', geo='SA')
        df = pytrends.interest_over_time()
        if df.empty:
            log.info(f'  0 points')
            return []
        df = df.drop(columns=['isPartial'], errors='ignore')
        records = []
        for date_idx, row in df.iterrows():
            val = int(row[keyword]) if keyword in row else 0
            if val > 0:
                records.append({'keyword':keyword,'category':category,'date':date_idx.strftime('%Y-%m-%d'),'interest':val,'geo':'SA','fetched_at':datetime.now(timezone.utc).isoformat()})
        log.info(f'  {len(records)} points')
        return records
    except Exception as e:
        log.error(f'Pytrends Error {keyword}: {e}')
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

    for category, groups in KEYWORD_GROUPS.items():
        for kw in groups['serpapi']:
            all_interest.extend(fetch_serpapi_interest(kw, category))
            all_related.extend(fetch_serpapi_related(kw, category))
            time.sleep(2)
        for kw in groups['pytrends']:
            all_interest.extend(fetch_pytrends_interest(kw, category))

    trending = fetch_trending()
    save('trends_interest', all_interest)
    save('trends_trending', trending)
    save('trends_related', all_related)
    log.info('Done!')

if __name__ == '__main__':
    main()
