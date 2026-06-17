"""
Google Trends Fetcher — trends_fetcher.py
"""

import os
import json
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

pytrends = TrendReq(hl="ar", tz=180, timeout=(10, 25), retries=3, backoff_factor=0.5)
TIMEFRAME = "today 3-m"

KEYWORD_GROUPS = {
    "geopolitical": ["Iran war", "Israel Gaza", "Middle East conflict", "حرب إيران", "غزة"],
    "economic": ["Saudi Aramco", "oil price", "NEOM", "Vision 2030", "سعر النفط"],
    "saudi_local": ["رؤية 2030", "نيوم", "الرياض", "السعودية", "وزارة المالية"]
}

def fetch_interest_over_time(keywords, category):
    chunks = [keywords[i:i+5] for i in range(0, len(keywords), 5)]
    records = []
    for chunk in chunks:
        try:
            pytrends.build_payload(chunk, timeframe=TIMEFRAME, geo="SA")
            df = pytrends.interest_over_time()
            if df.empty:
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
            time.sleep(2)
        except Exception as e:
            log.error(f"خطأ: {e}")
            time.sleep(5)
    return records

def fetch_trending_now(geo="SA"):
    try:
        df = pytrends.trending_searches(pn="saudi_arabia")
        return [{"keyword": row, "rank": i+1, "geo": geo,
                 "fetched_at": datetime.now(timezone.utc).isoformat()}
                for i, row in enumerate(df[0].tolist())]
    except Exception as e:
        log.error(f"خطأ Trending: {e}")
        return []

def fetch_related_queries(keywords, category):
    records = []
    chunks = [keywords[i:i+5] for i in range(0, len(keywords), 5)]
    for chunk in chunks:
        try:
            pytrends.build_payload(chunk, timeframe=TIMEFRAME, geo="SA")
            related = pytrends.related_queries()
            for kw in chunk:
                if kw not in related:
                    continue
                for query_type in ["top", "rising"]:
                    df = related[kw].get(query_type)
                    if df is None or df.empty:
                        continue
                    for _, row in df.iterrows():
                        records.append({
                            "main_keyword": kw, "related_query": row["query"],
                            "value": int(row["value"]), "query_type": query_type,
                            "category": category,
                            "fetched_at": datetime.now(timezone.utc).isoformat()
                        })
            time.sleep(2)
        except Exception as e:
            log.error(f"خطأ Related: {e}")
            time.sleep(5)
    return records

def upsert_to_supabase(table, records):
    if not records:
        return
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        supabase.table(table).delete().gte("fetched_at", today).execute()
        for i in range(0, len(records), 50):
            supabase.table(table).insert(records[i:i+50]).execute()
            log.info(f"✅ {len(records[i:i+50])} سجل في {table}")
    except Exception as e:
        log.error(f"خطأ Supabase: {e}")
        raise

def main():
    log.info("🚀 بدأ الجلب...")
    all_interest, all_related = [], []
    for category, keywords in KEYWORD_GROUPS.items():
        log.info(f"📊 {category}")
        all_interest.extend(fetch_interest_over_time(keywords, category))
        all_related.extend(fetch_related_queries(keywords, category))
        time.sleep(3)
    trending = fetch_trending_now()
    upsert_to_supabase("trends_interest", all_interest)
    upsert_to_supabase("trends_trending", trending)
    upsert_to_supabase("trends_related", all_related)
    log.info("✅ اكتمل")

if __name__ == "__main__":
    main()
