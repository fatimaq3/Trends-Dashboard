"""
build_dashboard.py — v3 (Live Supabase)
الداشبورد يسحب البيانا֪ من Supabase مباشرة عبر JavaScript
"""

import os
from datetime import datetime, timezone

SUPABASE_URL = "https://tkmatxmnmphmuykhywtv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRrbWF0eG1ubXBobXV5a2h5d3R2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA0MDM1NDgsImV4cCI6MjA5NTk3OTU0OH0.NUwIIhKfqILel1a12HL2NYS-R-iky0E2U7o9tlgtKac"

def build_dashboard():
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>TrendsWatch 🇸🇦</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{{
  --bg:#F8F7F2;--surface:#FFFFFF;--border:#E2DDD0;--text:#1A1A14;--muted:#6B6860;
  --green:#286140;--green-light:#EBF3ED;
  --gold:#B58500;--gold-light:#FBF3D5;--gold-dark:#7A4700;
  --red:#A32D2D;--red-light:#FCEBEB;--red-border:#F09595;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',Tahoma,Arial,sans-serif}}
header{{background:var(--green);color:#fff;padding:18px 28px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px}}
.logo{{font-size:1.3rem;font-weight:600;display:flex;align-items:center;gap:8px}}
.logo-accent{{color:#B58500}}
.updated{{font-size:12px;opacity:.8}}
main{{max-width:1300px;margin:0 auto;padding:24px 20px;display:grid;gap:24px}}
.sec-label{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin-bottom:12px;display:flex;align-items:center;gap:8px}}
.sec-label::after{{content:'';flex:1;height:1px;background:var(--border)}}
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}}
.kpi{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px 16px;border-top:3px solid var(--green)}}
.kpi-label{{font-size:11px;color:var(--muted);margin-bottom:4px}}
.kpi-val{{font-size:24px;font-weight:600;color:var(--green)}}
.kpi-sub{{font-size:11px;color:var(--muted);margin-top:3px}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 18px}}
.alert{{background:var(--red-light);border:1px solid var(--red-border);border-radius:8px;padding:10px 14px;font-size:13px;color:var(--red);display:flex;align-items:center;gap:8px;margin-bottom:8px;font-weight:500}}
.chip{{display:inline-flex;align-items:center;gap:4px;padding:5px 12px;border-radius:20px;font-size:12px;border:1px solid var(--border);background:var(--bg);cursor:pointer;transition:all .15s;color:var(--muted)}}
.chip.active{{background:var(--green);border-color:var(--green);color:#fff}}
.chips{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}}
.kw-row{{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid var(--border)}}
.kw-row:last-child{{border-bottom:none}}
.kw-rank{{font-size:12px;font-weight:600;color:var(--gold);min-width:22px}}
.kw-name{{font-size:13px;flex:1}}
.kw-bar-bg{{flex:1;height:5px;background:var(--border);border-radius:3px;overflow:hidden}}
.kw-bar{{height:5px;border-radius:3px;background:var(--green)}}
.kw-val{{font-size:12px;color:var(--muted);min-width:28px;text-align:left}}
.leg{{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--muted);margin-top:8px}}
.leg-grad{{width:80px;height:7px;border-radius:4px;background:linear-gradient(to left,#286140,#EBF3ED)}}
.leg-dot{{width:10px;height:10px;border-radius:2px;display:inline-block;margin-left:4px}}
.cmp-legend{{display:flex;gap:12px;font-size:12px;color:var(--muted);margin-bottom:8px;flex-wrap:wrap}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.rising-row{{display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid var(--border);font-size:13px}}
.rising-row:last-child{{border-bottom:none}}
.rising-pct{{color:var(--green);font-size:11px;font-weight:600;min-width:50px;text-align:left}}
.tag{{display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:20px;font-size:11px;background:var(--green-light);border:1px solid #9FE1CB;color:var(--green);margin:2px}}
.filter-row{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:10px}}
.filter-row select{{padding:5px 8px;font-size:12px;border:1px solid var(--border);border-radius:8px;background:var(--bg);color:var(--text)}}
.badge-geo{{background:#E6F1FB;color:#0C447C;font-size:11px;padding:2px 7px;border-radius:4px}}
.badge-eco{{background:var(--gold-light);color:var(--gold-dark);font-size:11px;padding:2px 7px;border-radius:4px}}
.badge-sa{{background:var(--green-light);color:var(--green);font-size:11px;padding:2px 7px;border-radius:4px}}
.loading{{text-align:center;padding:40px;color:var(--muted);font-size:14px}}
.spinner{{display:inline-block;width:24px;height:24px;border:3px solid var(--border);border-top-color:var(--green);border-radius:50%;animation:spin .8s linear infinite;margin-bottom:8px}}
@keyframes spin{{to{{transform:rotate(360px)}}}}
.heatmap{{display:grid;grid-template-columns:repeat(7,1fr);gap:3px;margin-top:8px}}
.hm-cell{{height:28px;border-radius:3px}}
.hm-days{{display:grid;grid-template-columns:repeat(7,1fr);gap:3px;margin-bottom:5px}}
.hm-day{{font-size:10px;color:var(--muted);text-align:center}}
@media(max-width:700px){{.grid2{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header>
  <div class="logo">📈 Trends<span class="logo-accent">Watch</span> 🇸🇦</div>
  <div class="updated" id="updatedAt">جاري التحميل...</div>
</header>
<main id="mainContent">
  <div class="loading"><div class="spinner"></div><br>جاري تحميل البيانات من Supabase...</div>
</main>

<script>
const SUPABASE_URL = '{SUPABASE_URL}';
const SUPABASE_KEY = '{SUPABASE_ANON_KEY}';
const COLORS = ['#286140','#B58500','#A32D2D','#185FA5','#534AB7','#0F6E56','#993556','#7A4700'];
const CAT_AR = {{'geopolitical':'جيوسياسي','economic':'اقتصادي','saudi_local':'محلي'}};

async function sbFetch(table, params='') {{
  const res = await fetch(`${{SUPABASE_URL}}/rest/v1/${{table}}?${{params}}`, {{
    headers: {{
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${{SUPABASE_KEY}}`
    }}
  }});
  return res.json();
}}

async function loadData() {{
  const [interest, trending, related] = await Promise.all([
    sbFetch('trends_interest', 'select=keyword,category,date,interest&order=date.asc&limit=2000'),
    sbFetch('trends_trending', 'select=keyword,rank&order=rank.asc&limit=20'),
    sbFetch('trends_related', 'select=main_keyword,related_query,value,query_type,category&query_type=eq.rising&order=value.desc&limit=30')
  ]);
  return {{ interest, trending, related }};
}}

function buildKwMap(interest) {{
  const map = {{}};
  for (const row of interest) {{
    if (!map[row.keyword]) map[row.keyword] = {{ cat: row.category, dates: [], values: [] }};
    map[row.keyword].dates.push(row.date);
    map[row.keyword].values.push(row.interest);
  }}
  return map;
}}

function catClass(c) {{
  return c==='geopolitical'?'badge-geo':c==='economic'?'badge-eco':'badge-sa';
}}

let mainChart = null, cmpChart = null;
let KW_DATA = {{}}, TRENDING = [], RELATED = [];
let activeKws = [], activeCat = 'all';

function getLabels(kwMap) {{
  const allDates = new Set();
  for (const kw of Object.values(kwMap)) kw.dates.forEach(d => allDates.add(d));
  return Array.from(allDates).sort();
}}

function getValues(kwData, labels) {{
  const dateToVal = {{}};
  kwData.dates.forEach((d, i) => dateToVal[d] = kwData.values[i]);
  return labels.map(l => dateToVal[l] ?? 0);
}}

function filteredKws() {{
  return activeKws.filter(k => activeCat === 'all' || (KW_DATA[k] && KW_DATA[k].cat === activeCat));
}}

async function addKw(){{const inp=document.getElementById('kwInput'),v=inp.value.trim();if(!v)return;inp.value='';const rows=await sbFetch('trends_interest','select=keyword,category,date,interest&keyword=eq.'+encodeURIComponent(v)+'&order=date.asc&limit=200');if(rows&&rows.length){{if(!KW_DATA[v]){{KW_DATA[v]={{cat:rows[0].category,dates:[],values:[]}};rows.forEach(r=>{{KW_DATA[v].dates.push(r.date);KW_DATA[v].values.push(r.interest);}});}}if(!activeKws.includes(v))activeKws.push(v);}}else{{KW_DATA[v]={{cat:'saudi_local',dates:CURRENT_LABELS,values:Array(CURRENT_LABELS.length).fill(0)}};if(!activeKws.includes(v))activeKws.push(v);}}renderKwTags();renderMainChart(CURRENT_LABELS);}}
function renderKwTags() {{
  document.getElementById('kwTags').innerHTML = filteredKws().map(k =>
    `<span class="tag"><span class="${{catClass(KW_DATA[k]?.cat||'saudi_local')}}">${{CAT_AR[KW_DATA[k]?.cat]||''}}</span> ${{k}}</span>`
  ).join('');
}}

function renderMainChart(labels) {{
  const kws = filteredKws().slice(0, 6);
  const datasets = kws.map((k, i) => ({{
    label: k,
    data: getValues(KW_DATA[k], labels),
    borderColor: COLORS[i % COLORS.length],
    backgroundColor: COLORS[i % COLORS.length] + '15',
    borderWidth: 2, pointRadius: 0, fill: false, tension: 0.4
  }}));
  document.getElementById('mainLegend').innerHTML = kws.map((k, i) =>
    `<span style="display:flex;align-items:center;gap:4px"><span class="leg-dot" style="background:${{COLORS[i%COLORS.length]}}"></span>${{k}}</span>`
  ).join('');
  if (mainChart) mainChart.destroy();
  mainChart = new Chart(document.getElementById('mainChart'), {{
    type: 'line',
    data: {{ labels, datasets }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }}, tooltip: {{ mode: 'index', intersect: false }} }},
      scales: {{
        x: {{ ticks: {{ maxTicksLimit: 8, color: '#6B6860', font: {{ size: 10 }} }}, grid: {{ color: 'rgba(0,0,0,.06)' }} }},
        y: {{ min: 0, max: 100, ticks: {{ color: '#6B6860', font: {{ size: 10 }} }}, grid: {{ color: 'rgba(0,0,0,.06)' }} }}
      }}
    }}
  }});
}}

function updateCompare(labels) {{
  const k1 = document.getElementById('cmp1')?.value || activeKws[0];
  const k2 = document.getElementById('cmp2')?.value || activeKws[1] || activeKws[0];
  const d1 = KW_DATA[k1] ? getValues(KW_DATA[k1], labels) : Array(labels.length).fill(0);
  const d2 = KW_DATA[k2] ? getValues(KW_DATA[k2], labels) : Array(labels.length).fill(0);
  document.getElementById('cmpLegend').innerHTML =
    `<span><span class="leg-dot" style="background:#286140"></span>${{k1}}</span><span><span class="leg-dot" style="background:#B58500"></span>${{k2}}</span>`;
  if (cmpChart) cmpChart.destroy();
  cmpChart = new Chart(document.getElementById('cmpChart'), {{
    type: 'line',
    data: {{ labels, datasets: [
      {{ label: k1, data: d1, borderColor: '#286140', backgroundColor: '#28614015', borderWidth: 2, pointRadius: 0, tension: 0.4 }},
      {{ label: k2, data: d2, borderColor: '#B58500', backgroundColor: '#B5850015', borderWidth: 2, pointRadius: 0, tension: 0.4, borderDash: [5,3] }}
    ]}},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ ticks: {{ maxTicksLimit: 5, color: '#6B6860', font: {{ size: 10 }} }}, grid: {{ color: 'rgba(0,0,0,.06)' }} }},
        y: {{ min: 0, max: 100, ticks: {{ color: '#6B6860', font: {{ size: 10 }} }}, grid: {{ color: 'rgba(0,0,0,.06)' }} }}
      }}
    }}
  }});
}}

function renderTrending() {{
  if (!TRENDING.length) {{ document.getElementById('trendingList').innerHTML = '<p style="font-size:13px;color:#6B6860;padding:8px 0">لا بيانات متاحة</p>'; return; }}
  document.getElementById('trendingList').innerHTML = TRENDING.map((t, i) =>
    `<div class="kw-row"><span class="kw-rank">#${{t.rank||i+1}}</span><span class="kw-name">${{t.keyword}}</span><span style="font-size:11px;color:${{i<3?'#A32D2D':'#6B6860'}}">${{i<3?'🔴':''}}</span></div>`
  ).join('');
}}

function renderRising() {{
  if (!RELATED.length) {{ document.getElementById('risingList').innerHTML = '<p style="font-size:13px;color:#6B6860;padding:8px 0">لا بيانات متاحة</p>'; return; }}
  document.getElementById('risingList').innerHTML = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">' +
    RELATED.map(r =>
      `<div class="rising-row"><span class="${{catClass(r.category)}}" style="min-width:48px">${{CAT_AR[r.category]||''}}</span><span style="flex:1;font-size:12px">${{r.related_query}}</span><span class="rising-pct">↑${{r.value}}%</span></div>`
    ).join('') + '</div>';
}}

function renderSpikes() {{
  const spikes = [];
  for (const [kw, d] of Object.entries(KW_DATA)) {{
    if (d.values.length >= 14) {{
      const recent = d.values.slice(-7), prev = d.values.slice(-14, -7);
      const diff = Math.round(recent.reduce((a,b)=>a+b,0)/recent.length - prev.reduce((a,b)=>a+b,0)/prev.length);
      if (diff > 30) spikes.push([kw, diff]);
    }}
  }}
  const sec = document.getElementById('alertsSection');
  if (!spikes.length) {{ sec.style.display = 'none'; return; }}
  sec.style.display = '';
  document.getElementById('alertsList').innerHTML = spikes.map(([kw, diff]) =>
    `<div class="alert">🔴 <strong>${{kw}}</strong> — ارتفص ${{diff}}+ نقطة في آخر 7 أيام</div>`
  ).join('');
  document.getElementById('spikeCount').textContent = spikes.length;
}}

function renderHeatmap(labels) {{
  const kw = document.getElementById('hmKw')?.value || activeKws[0];
  const vals = KW_DATA[kw] ? getValues(KW_DATA[kw], labels).slice(-28) : Array(28).fill(0);
  const mx = Math.max(...vals, 1);
  document.getElementById('heatmapGrid').innerHTML = vals.map(v => {{
    const alpha = (0.15 + (v/mx) * 0.85).toFixed(2);
    return `<div class="hm-cell" style="background:rgba(40,97,64,${{alpha}})" title="${{v}}"></div>`;
  }}).join('');
}}

function buildUI(kwMap, labels) {{
  const kwKeys = Object.keys(kwMap);
  const topTerm = kwKeys.reduce((a, b) => (Math.max(...(kwMap[b]?.values||[0])) > Math.max(...(kwMap[a]?.values||[0])) ? b : a), kwKeys[0] || '—');
  const allVals = Object.values(kwMap).flatMap(d => d.values);
  const avgInterest = allVals.length ? Math.round(allVals.reduce((a,b)=>a+b,0)/allVals.length) : 0;

  document.getElementById('mainContent').innerHTML = `
  <section>
    <div class="sec-label">📊 ملخص / Summary</div>
    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-label">أعلى مصطلح / Top term</div><div class="kpi-val" style="font-size:16px;margin-top:4px">${{topTerm}}</div></div>
      <div class="kpi"><div class="kpi-label">مصطلحات / Tracked</div><div class="kpi-val">${{kwKeys.length}}</div><div class="kpi-sub">عبر 3 فئات</div></div>
      <div class="kpi" style="border-top-color:var(--red)"><div class="kpi-label">ارتفاع مفاجئ / Spikes</div><div class="kpi-val" style="color:var(--red)" id="spikeCount">0</div><div class="kpi-sub">آخر 7 أيام</div></div>
      <div class="kpi" style="border-top-color:var(--gold)"><div class="kpi-label">متوسط / Avg interest</div><div class="kpi-val" style="color:var(--gold-dark)">${{avgInterest}}</div><div class="kpi-sub">من 100</div></div>
    </div>
  </section>

  <section id="alertsSection" style="display:none">
    <div class="sec-label">🚨 تنبيهات / Alerts</div>
    <div id="alertsList"></div>
  </section>

  <section>
    <div class="sec-label">🏷️ الكلمات المفتاحية / Keywords</div>
    <div class="card">
      <div class="chips" id="catChips">
        <span class="chip active" onclick="filterCat('all',this)">الكل / All</span>
        <span class="chip" onclick="filterCat('geopolitical',this)">جيوسياسي</span>
        <span class="chip" onclick="filterCat('economic',this)">اقتصادي</span>
        <span class="chip" onclick="filterCat('saudi_local',this)">محلي</span>
      </div>
      <div id="kwTags"></div>
      <div class="add-kw">
        <input type="text" id="kwInput" placeholder="أضف كلمة... / Add keyword..." onkeydown="if(event.key==='Enter')addKw()">
        <button onclick="addKw()">+ إضافة</button>
      </div>
    </div>
  </section>

  <section>
    <div class="sec-label">📈 الاهتمام عبر الزمن / Interest over time</div>
    <div class="card">
      <div class="cmp-legend" id="mainLegend"></div>
      <div style="position:relative;width:100%;height:240px">
        <canvas id="mainChart"></canvas>
      </div>
    </div>
  </section>

  <div class="grid2">
    <section>
      <div class="sec-label">⚖️ مقارنة / Compare</div>
      <div class="card">
        <div class="filter-row">
          <select id="cmp1" onchange="updateCompare(CURRENT_LABELS)">${{kwKeys.map(k=>`<option>${{k}}</option>`).join('')}}</select>
          <span style="font-size:13px;color:var(--muted)">vs</span>
          <select id="cmp2" onchange="updateCompare(CURRENT_LABELS)">${{kwKeys.slice(1).map(k=>`<option>${{k}}</option>`).join('')}}</select>
        </div>
        <div class="cmp-legend" id="cmpLegend"></div>
        <div style="position:relative;width:100%;height:180px"><canvas id="cmpChart"></canvas></div>
      </div>
    </section>
    <section>
      <div class="sec-label">🔥 الأكثر بحثاً الآن / Trending now</div>
      <div class="card" style="max-height:300px;overflow-y:auto"><div id="trendingList"></div></div>
    </section>
  </div>

  <div class="grid2">
    <section>
      <div class="sec-label">📅 Heatmap أسبوعي</div>
      <div class="card">
        <div class="filter-row"><select id="hmKw" onchange="renderHeatmap(CURRENT_LABELS)">${{kwKeys.map(k=>`<option>${{k}}</option>`).join('')}}</select></div>
        <div class="hm-days"><div class="hm-day">سبت</div><div class="hm-day">أحد</div><div class="hm-day">اثنين</div><div class="hm-day">ثلاثاء</div><div class="hm-day">أربعاء</div><div class="hm-day">خميس</div><div class="hm-day">جمعة</div></div>
        <div class="heatmap" id="heatmapGrid"></div>
        <div class="leg"><span>منخفض</span><div class="leg-grad"></div><span>مرتفص</span></div>
      </div>
    </section>
    <section>
      <div class="sec-label">🚀 استفسارا֪ صاعدة / Rising queries</div>
      <div class="card"><div id="risingList"></div></div>
    </section>
  </div>`;

  window.filterCat = function(cat, el) {{
    activeCat = cat;
    document.querySelectorAll('#catChips .chip').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    renderKwTags();
    renderMainChart(CURRENT_LABELS);
  }};
}}

let CURRENT_LABELS = [];

async function init() {{
  try {{
    const {{ interest, trending, related }} = await loadData();
    KW_DATA = buildKwMap(interest);
    TRENDING = trending;
    RELATED = related;
    activeKws = Object.keys(KW_DATA);
    CURRENT_LABELS = getLabels(KW_DATA);

    buildUI(KW_DATA, CURRENT_LABELS);

    const now = new Date();
    document.getElementById('updatedAt').textContent =
      'آخر تحديث: ' + now.toLocaleString('ar-SA', {{timeZone:'Asia/Riyadh'}});

    renderKwTags();
    renderMainChart(CURRENT_LABELS);
    updateCompare(CURRENT_LABELS);
    renderTrending();
    renderHeatmap(CURRENT_LABELS);
    renderRising();
    renderSpikes();

    // تحديث تلقائي كل 5 دفائق
    setInterval(async () => {{
      const {{ interest: ni, trending: nt, related: nr }} = await loadData();
      KW_DATA = buildKwMap(ni);
      TRENDING = nt;
      RELATED = nr;
      CURRENT_LABELS = getLabels(KW_DATA);
      renderMainChart(CURRENT_LABELS);
      updateCompare(CURRENT_LABELS);
      renderTrending();
      renderHeatmap(CURRENT_LABELS);
      renderRising();
      renderSpikes();
      document.getElementById('updatedAt').textContent =
        'آخر تحديث: ' + new Date().toLocaleString('ar-SA', {{timeZone:'Asia/Riyadh'}});
    }}, 5 * 60 * 1000);

  }} catch(e) {{
    document.getElementById('mainContent').innerHTML =
      `<div class="loading" style="color:var(--red)">❌ خطأ في تحميل البيانات: ${{e.message}}</div>`;
  }}
}}

init();
</script>
</body>
</html>"""

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Dashboard v3 (Live) → docs/index.html")

if __name__ == "__main__":
    build_dashboard()
