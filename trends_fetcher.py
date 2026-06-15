import os
import time
import logging
from datetime import datetime, timezone
from pytrends.request import TrendReq
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

pytrends = TrendReq(
    hl="ar", tz=180,
    timeout=(10, 25),
    retries=3,
    backoff_factor=1,
    requests_args={
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8"
        }
    }
)

TIMEFRAME = "today 3-m"

KEYWORD_GROUPS = {
    "geopolitical": ["Iran war", "Israel Gaza", "حرب إيران", "غزة"],
    "economic":     ["Saudi Aramco", "oil price", "Vision 2030", "سعر النفط"],
    "saudi_local":  ["رؤية 2030", "نيوم", "السعودية", "الرياض"]
}

def fetch_interest(keywords, category):
    records = []
    chunks = [keywords[i:i+4] for i in range(0, len(keywords), 4)]
    for chunk in chunks:
        try:
            log.info(f"Fetching: {chunk}")
            pytrends.build_payload(chunk, timeframe=TIMEFRAME, geo="SA")
            df = pytrends.interest_over_time()
            if df.empty:
                log.warning(f"Empty result for {chunk}")
                continue
            df = df.drop(columns=["isPartial"], errors="ignore")
            for date_idx, row in df.iterrows():
                for kw in chunk:
                    if kw in row:
                        records.append({
                            "keyword": kw, "category": category,
                            "date": date_idx.strftime("%Y-%m-%d"),
                            "interest": int(row[kw]), "geo": "SA",
                            "fetched_at": datetime.now(timezone.utc).isoformat()
                        })
            time.sleep(4)
        except Exception as e:
            log.error(f"Error {chunk}: {e}")
            time.sleep(10)
    return records

def fetch_trending():
    try:
        df = pytrends.trending_searches(pn="saudi_arabia")
        return [{"keyword": row, "rank": i+1, "geo": "SA",
                 "fetched_at": datetime.now(timezone.utc).isoformat()}
                for i, row in enumerate(df[0].tolist())]
    except Exception as e:
        log.error(f"Trending error: {e}")
        return []

def fetch_related(keywords, category):
    records = []
    chunks = [keywords[i:i+4] for i in range(0, len(keywords), 4)]
    for chunk in chunks:
        try:
            pytrends.build_payload(chunk, timeframe=TIMEFRAME, geo="SA")
            related = pytrends.related_queries()
            for kw in chunk:
                if kw not in related:
                    continue
                for qtype in ["top", "rising"]:
                    df = related[kw].get(qtype)
                    if df is None or df.empty:
                        continue
                    for _, row in df.iterrows():
                        records.append({
                            "main_keyword": kw, "related_query": row["query"],
                            "value": int(row["value"]), "query_type": qtype,
                            "category": category,
                            "fetched_at": datetime.now(timezone.utc).isoformat()
                        })
            time.sleep(4)
        except Exception as e:
            log.error(f"Related error {chunk}: {e}")
            time.sleep(10)
    return records

def save(table, records):
    if not records:
        log.info(f"No records for {table}")
        return
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        supabase.table(table).delete().gte("fetched_at", today).execute()
        for i in range(0, len(records), 50):
            supabase.table(table).insert(records[i:i+50]).execute()
        log.info(f"✅ Saved {len(records)} → {table}")
    except Exception as e:
        log.error(f"Supabase error ({table}): {e}")
        raise

def main():
    log.info("🚀 Starting fetch...")
    all_interest, all_related = [], []
    for category, keywords in KEYWORD_GROUPS.items():
        log.info(f"Category: {category}")
        all_interest.extend(fetch_interest(keywords, category))
        all_related.extend(fetch_related(keywords, category))
        time.sleep(5)
    trending = fetch_trending()
    save("trends_interest", all_interest)
    save("trends_trending", trending)
    save("trends_related", all_related)
    log.info("✅ Done!")

if __name__ == "__main__":
    main()
