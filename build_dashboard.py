"""
build_dashboard.py
"""

import os
import json
from datetime import datetime, timezone
from supabase import create_client, Client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

COLORS = ["#3B82F6","#10B981","#F59E0B","#EF4444","#8B5CF6","#06B6D4"]
CAT_LABELS = {"geopolitical":"جيوسياسي 🌍","economic":"اقتصادي 📈","saudi_local":"سعودي محلي 🇸🇦"}

def fetch_data():
    interest = supabase.table("trends_interest").select("keyword,category,date,interest").order("date").execute().data or []
    trending = supabase.table("trends_trending").select("keyword,rank").order("rank").limit(20).execute().data or []
    related  = supabase.table("trends_related").select("main_keyword,related_query,value,query_type,category").eq("query_type","rising").order("value",desc=True).limit(50).execute().data or []
    return interest, trending, related

def build_dashboard(interest_data, trending_data, related_data):
    updated_at = datetime.now(timezone.utc).strftime("%d %b %Y — %H:%M UTC")
    categories = {}
    for row in interest_data:
        cat, kw = row["category"], row["keyword"]
        if cat not in categories: categories[cat] = {}
        if kw not in categories[cat]: categories[cat][kw] = {"dates":[],"values":[]}
        categories[cat][kw]["dates"].append(row["date"])
        categories[cat][kw]["values"].append(row["interest"])

    charts_json   = json.dumps(categories, ensure_ascii=False)
    trending_json = json.dumps(trending_data, ensure_ascii=False)
    related_json  = json.dumps(related_data, ensure_ascii=False)

    tabs_html = "".join(
        f'<button class="tab {"active" if i==0 else ""}" data-cat="{cat}" onclick="switchCat(this)">{CAT_LABELS.get(cat,cat)}</button>'
        for i,cat in enumerate(categories.keys())
    )
    panels_html = "".join(
        f'''<div class="chart-panel {"active" if i==0 else ""}" id="panel-{cat}">
          <div class="chart-grid">
            {"".join(f'<div class="chart-card"><h3>{kw}</h3><canvas id="chart-{cat}-{j}"></canvas></div>' for j,kw in enumerate(kws.keys()))}
          </div></div>'''
        for i,(cat,kws) in enumerate(categories.items())
    )

    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>TrendsWatch 🇸🇦</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{{--bg:#0F1117;--surface:#1A1D27;--border:#2A2D3A;--accent:#3B82F6;--accent2:#10B981;--text:#E2E8F0;--muted:#64748B;--hot:#EF4444;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',Tahoma,Arial,sans-serif;}}
header{{padding:24px 32px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;}}
.logo{{font-size:1.4rem;font-weight:700;}}.logo span{{color:var(--accent);}}
.updated{{font-size:0.8rem;color:var(--muted);}}
main{{max-width:1400px;margin:0 auto;padding:32px 24px;display:grid;gap:32px;}}
.section-title{{font-size:1rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;display:flex;align-items:center;gap:8px;}}
.section-title::after{{content:'';flex:1;height:1px;background:var(--border);}}
.tabs{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px;}}
.tab{{padding:8px 18px;border-radius:20px;border:1px solid var(--border);background:transparent;color:var(--muted);cursor:pointer;font-size:0.9rem;transition:all 0.2s;}}
.tab.active{{background:var(--accent);border-color:var(--accent);color:#fff;}}
.tab:hover:not(.active){{border-color:var(--accent);color:var(--text);}}
.chart-panel{{display:none;}}.chart-panel.active{{display:block;}}
.chart-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:20px;}}
.chart-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;}}
.chart-card h3{{font-size:0.9rem;color:var(--muted);margin-bottom:14px;}}
.chart-card canvas{{max-height:200px;}}
.trending-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;}}
.trend-item{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px 16px;display:flex;align-items:center;gap:12px;transition:border-color 0.2s;}}
.trend-item:hover{{border-color:var(--accent);}}
.trend-rank{{font-size:1.1rem;font-weight:700;color:var(--accent);min-width:28px;}}
.trend-rank.hot{{color:var(--hot);}}
.trend-kw{{font-size:0.9rem;}}
.related-table{{width:100%;border-collapse:collapse;}}
.related-table th{{text-align:right;padding:10px 14px;font-size:0.8rem;color:var(--muted);border-bottom:1px solid var(--border);}}
.related-table td{{padding:10px 14px;font-size:0.9rem;border-bottom:1px solid var(--border);}}
.related-table tr:last-child td{{border-bottom:none;}}
.badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:0.75rem;background:rgba(16,185,129,0.15);color:var(--accent2);}}
.bar-bg{{background:var(--border);border-radius:4px;height:6px;width:120px;}}
.bar-fill{{background:var(--accent2);border-radius:4px;height:6px;}}
</style>
</head>
<body>
<header>
  <div class="logo">Trends<span>Watch</span> 🇸🇦</div>
  <div class="updated">آخر تحديث: {updated_at}</div>
</header>
<main>
  <section>
    <div class="section-title">الاهتمام عبر الزمن — آخر 90 يوم</div>
    <div class="tabs">{tabs_html}</div>
    {panels_html}
  </section>
  <section>
    <div class="section-title">🔥 الأكثر بحثاً الآن في السعودية</div>
    <div class="trending-grid" id="trendingGrid"></div>
  </section>
  <section>
    <div class="section-title">📡 استفسارات صاعدة مرتبطة</div>
    <div class="chart-card" style="overflow-x:auto">
      <table class="related-table">
        <thead><tr><th>الكلمة الرئيسية</th><th>الاستفسار</th><th>الفئة</th><th>الارتفاع</th></tr></thead>
        <tbody id="relatedBody"></tbody>
      </table>
    </div>
  </section>
</main>
<script>
const CHARTS_DATA={charts_json};
const TRENDING={trending_json};
const RELATED={related_json};
const COLORS={json.dumps(COLORS)};
const CI={{}};
function drawChartsForCat(cat){{
  const kws=CHARTS_DATA[cat];if(!kws)return;
  Object.entries(kws).forEach(([kw,data],j)=>{{
    const id=`chart-${{cat}}-${{j}}`,canvas=document.getElementById(id);
    if(!canvas)return;if(CI[id])CI[id].destroy();
    CI[id]=new Chart(canvas,{{type:'line',data:{{labels:data.dates,datasets:[{{label:kw,data:data.values,borderColor:COLORS[j%COLORS.length],backgroundColor:COLORS[j%COLORS.length]+'22',borderWidth:2,pointRadius:0,fill:true,tension:0.4}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{x:{{ticks:{{maxTicksLimit:6,color:'#64748B',font:{{size:10}}}},grid:{{color:'#2A2D3A'}}}},y:{{min:0,max:100,ticks:{{color:'#64748B',font:{{size:10}}}},grid:{{color:'#2A2D3A'}}}}}}}}}});
  }});
}}
function switchCat(btn){{
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.chart-panel').forEach(p=>p.classList.remove('active'));
  btn.classList.add('active');
  const cat=btn.dataset.cat;
  document.getElementById(`panel-${{cat}}`).classList.add('active');
  drawChartsForCat(cat);
}}
const CAT_AR={{geopolitical:'جيوسياسي',economic:'اقتصادي',saudi_local:'محلي'}};
function renderTrending(){{
  document.getElementById('trendingGrid').innerHTML=TRENDING.map(t=>`<div class="trend-item"><span class="trend-rank ${{t.rank<=3?'hot':''}}">#${{t.rank}}</span><span class="trend-kw">${{t.keyword}}</span></div>`).join('');
}}
function renderRelated(){{
  const maxVal=Math.max(...RELATED.map(r=>r.value),1);
  document.getElementById('relatedBody').innerHTML=RELATED.slice(0,30).map(r=>`<tr><td>${{r.main_keyword}}</td><td>${{r.related_query}}</td><td><span class="badge">${{CAT_AR[r.category]||r.category}}</span></td><td><div class="bar-bg"><div class="bar-fill" style="width:${{Math.round(r.value/maxVal*100)}}%"></div></div></td></tr>`).join('');
}}
(function init(){{
  const first=Object.keys(CHARTS_DATA)[0];
  if(first)drawChartsForCat(first);
  renderTrending();renderRelated();
}})();
</script>
</body>
</html>"""

    os.makedirs("docs",exist_ok=True)
    with open("docs/index.html","w",encoding="utf-8") as f:
        f.write(html)
    print("✅ Dashboard → docs/index.html")

if __name__ == "__main__":
    interest, trending, related = fetch_data()
    build_dashboard(interest, trending, related)
