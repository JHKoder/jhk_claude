#!/usr/bin/env python3
"""experiment.db → report.html 생성 후 브라우저 오픈."""
import json
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "collectors"))
from store import all_runs, get_claude_md_snapshots

OUT = Path(__file__).parent / "report.html"


def build_report():
    runs = all_runs()
    if not runs:
        print("저장된 실험 없음")
        sys.exit(0)

    snapshots = get_claude_md_snapshots()
    snapshot_hashes = [s["hash"] for s in snapshots]

    # CLAUDE.md 변경 기준으로 그룹 분류
    groups: dict[str, list] = {}
    for r in reversed(runs):
        h = r.get("claude_md_hash") or "unknown"
        groups.setdefault(h, []).append(r)

    runs_json = json.dumps(runs, ensure_ascii=False, default=str)
    groups_json = json.dumps(
        {k: [r["id"] for r in v] for k, v in groups.items()},
        ensure_ascii=False,
    )
    snapshots_json = json.dumps(snapshots, ensure_ascii=False, default=str)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>Experiment Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f1117; color: #e2e8f0; font-size: 14px; }}
  header {{ padding: 24px 32px; border-bottom: 1px solid #2d3748; }}
  header h1 {{ font-size: 20px; font-weight: 600; color: #fff; }}
  header p  {{ color: #718096; margin-top: 4px; font-size: 12px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
           padding: 24px 32px; }}
  .card {{ background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px;
           padding: 20px; }}
  .card.full {{ grid-column: 1 / -1; }}
  .card h2 {{ font-size: 13px; font-weight: 600; color: #a0aec0;
              text-transform: uppercase; letter-spacing: .05em; margin-bottom: 16px; }}
  .stat-row {{ display: flex; gap: 24px; flex-wrap: wrap; margin-bottom: 16px; }}
  .stat {{ text-align: center; }}
  .stat .val {{ font-size: 28px; font-weight: 700; color: #63b3ed; }}
  .stat .lbl {{ font-size: 11px; color: #718096; margin-top: 2px; }}
  canvas {{ max-height: 240px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th {{ text-align: left; padding: 8px 10px; color: #718096; border-bottom: 1px solid #2d3748;
        font-weight: 500; white-space: nowrap; }}
  td {{ padding: 8px 10px; border-bottom: 1px solid #1e2535; vertical-align: top; }}
  tr:hover td {{ background: #1e2535; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 99px;
            font-size: 11px; font-weight: 500; }}
  .badge.ok  {{ background: #22543d; color: #9ae6b4; }}
  .badge.fail {{ background: #742a2a; color: #feb2b2; }}
  .badge.na  {{ background: #2d3748; color: #718096; }}
  .stars {{ color: #f6e05e; }}
  .tag {{ display: inline-block; padding: 1px 6px; border-radius: 4px;
          background: #2d3748; color: #90cdf4; font-size: 10px; margin: 1px; }}
  .diff-line {{ font-size: 11px; color: #718096; }}
  .section-label {{ font-size: 11px; color: #f6ad55; font-weight: 600;
                    margin: 12px 0 6px; padding: 4px 8px;
                    background: #2d1b00; border-left: 3px solid #f6ad55;
                    border-radius: 0 4px 4px 0; }}
  .rating-btn {{ cursor: pointer; background: none; border: 1px solid #2d3748;
                 color: #718096; border-radius: 4px; padding: 2px 8px;
                 font-size: 11px; margin: 1px; }}
  .rating-btn:hover {{ border-color: #63b3ed; color: #63b3ed; }}
</style>
</head>
<body>
<header>
  <h1>Experiment Report</h1>
  <p id="subtitle"></p>
</header>

<div class="grid">

  <!-- 요약 통계 -->
  <div class="card">
    <h2>요약</h2>
    <div class="stat-row" id="summary-stats"></div>
  </div>

  <!-- CLAUDE.md 변경 효과 -->
  <div class="card">
    <h2>CLAUDE.md 변경 효과 (그룹별 평균 비용)</h2>
    <canvas id="groupChart"></canvas>
  </div>

  <!-- 토큰 트렌드 -->
  <div class="card">
    <h2>토큰 트렌드 (run 순서)</h2>
    <canvas id="tokenChart"></canvas>
  </div>

  <!-- 비용 vs 품질 -->
  <div class="card">
    <h2>비용 vs 품질 (버블: turn 수)</h2>
    <canvas id="scatterChart"></canvas>
  </div>

  <!-- 캐시 효율 -->
  <div class="card">
    <h2>캐시 효율 (cache_read / total_input)</h2>
    <canvas id="cacheChart"></canvas>
  </div>

  <!-- 품질 지표 -->
  <div class="card">
    <h2>품질 지표 트렌드</h2>
    <canvas id="qualityChart"></canvas>
  </div>

  <!-- 상세 테이블 -->
  <div class="card full">
    <h2>실험 상세</h2>
    <table id="runsTable">
      <thead>
        <tr>
          <th>#</th><th>날짜</th><th>Runner</th><th>Branch</th>
          <th>Turns</th><th>Output Tok</th><th>Cache Read</th>
          <th>Cost(USD)</th><th>Compile</th><th>Test%</th>
          <th>LOC +/-</th><th>Rating</th><th>Notes</th>
        </tr>
      </thead>
      <tbody id="runsBody"></tbody>
    </table>
  </div>

</div>

<script>
const RUNS = {runs_json};
const GROUPS = {groups_json};
const SNAPSHOTS = {snapshots_json};

// ── 유틸 ────────────────────────────────────────────────
const avg = arr => arr.length ? arr.reduce((a,b)=>a+b,0)/arr.length : 0;
const pct = (a,b) => b ? ((a-b)/b*100).toFixed(1)+'%' : 'n/a';
const stars = n => n ? '★'.repeat(n)+'☆'.repeat(5-n) : '—';
const fmt = (n,d=0) => n==null?'—':Number(n).toLocaleString('ko',{{maximumFractionDigits:d}});

// ── 요약 통계 ────────────────────────────────────────────
const totalCost = RUNS.reduce((s,r)=>s+(r.billing_usd||0),0);
const avgCacheHit = avg(RUNS.map(r=>{{
  const tot = (r.input_tokens||0)+(r.cache_read||0)+(r.cache_write||0);
  return tot ? (r.cache_read||0)/tot : 0;
}}));
const compileOk = RUNS.filter(r=>r.compile_ok).length;
const rated = RUNS.filter(r=>r.rating!=null);
const avgRating = rated.length ? avg(rated.map(r=>r.rating)) : null;

document.getElementById('subtitle').textContent =
  `${{RUNS.length}}개 실험  ·  총 ${{totalCost.toFixed(4)}} USD  ·  생성: ${{new Date().toLocaleString('ko')}}`;

document.getElementById('summary-stats').innerHTML = [
  ['총 비용', '$'+totalCost.toFixed(4)],
  ['평균 캐시 적중률', (avgCacheHit*100).toFixed(1)+'%'],
  ['컴파일 성공', compileOk+'/'+RUNS.length],
  ['평균 평점', avgRating!=null ? avgRating.toFixed(1)+' / 5' : '—'],
  ['총 실험 수', RUNS.length],
].map(([l,v])=>`<div class="stat"><div class="val">${{v}}</div><div class="lbl">${{l}}</div></div>`).join('');

// ── 색상 팔레트 ──────────────────────────────────────────
const PALETTE = ['#63b3ed','#68d391','#f6ad55','#fc8181','#b794f4','#76e4f7'];

// ── 그룹별 평균 비용 바 차트 ─────────────────────────────
const groupKeys = Object.keys(GROUPS);
const groupLabels = groupKeys.map((h,i)=>`그룹${{i+1}} (${{h.slice(0,6)}}…)`);
const groupAvgCost = groupKeys.map(h=>{{
  const ids = new Set(GROUPS[h]);
  const g = RUNS.filter(r=>ids.has(r.id));
  return avg(g.map(r=>r.billing_usd||0));
}});
new Chart(document.getElementById('groupChart'),{{
  type:'bar',
  data:{{ labels:groupLabels,
          datasets:[{{label:'평균 비용(USD)',data:groupAvgCost,
                      backgroundColor:PALETTE}}] }},
  options:{{ plugins:{{legend:{{display:false}}}},
             scales:{{ y:{{ ticks:{{color:'#718096'}}, grid:{{color:'#2d3748'}} }},
                       x:{{ ticks:{{color:'#718096'}}, grid:{{color:'#2d3748'}} }} }} }}
}});

// ── 토큰 트렌드 ──────────────────────────────────────────
const sorted = [...RUNS].reverse();
new Chart(document.getElementById('tokenChart'),{{
  type:'line',
  data:{{ labels: sorted.map(r=>'#'+r.id),
          datasets:[
            {{label:'Output',data:sorted.map(r=>r.output_tokens||0),
              borderColor:'#63b3ed',tension:.3,fill:false}},
            {{label:'Cache Read',data:sorted.map(r=>r.cache_read||0),
              borderColor:'#68d391',tension:.3,fill:false}},
            {{label:'Cache Write',data:sorted.map(r=>r.cache_write||0),
              borderColor:'#f6ad55',tension:.3,fill:false}},
          ] }},
  options:{{ plugins:{{legend:{{labels:{{color:'#a0aec0'}}}}}},
             scales:{{ y:{{ ticks:{{color:'#718096'}}, grid:{{color:'#2d3748'}} }},
                       x:{{ ticks:{{color:'#718096'}}, grid:{{color:'#2d3748'}} }} }} }}
}});

// ── 비용 vs 품질 산점도 ──────────────────────────────────
const scatter = RUNS.filter(r=>r.rating!=null).map(r=>{{
  return {{ x: r.billing_usd||0, y: r.rating||0, r: Math.max(4,(r.turn_count||0)/3) }};
}});
new Chart(document.getElementById('scatterChart'),{{
  type:'bubble',
  data:{{ datasets:[{{label:'실험',data:scatter,
                      backgroundColor:'rgba(99,179,237,.6)',
                      borderColor:'#63b3ed'}}] }},
  options:{{ plugins:{{legend:{{display:false}}}},
             scales:{{ y:{{title:{{display:true,text:'Rating',color:'#718096'}},
                           ticks:{{color:'#718096'}}, grid:{{color:'#2d3748'}},min:0,max:5}},
                       x:{{title:{{display:true,text:'Cost USD',color:'#718096'}},
                           ticks:{{color:'#718096'}}, grid:{{color:'#2d3748'}} }} }} }}
}});

// ── 캐시 효율 ────────────────────────────────────────────
const cacheRates = sorted.map(r=>{{
  const tot=(r.input_tokens||0)+(r.cache_read||0)+(r.cache_write||0);
  return tot ? +((r.cache_read||0)/tot*100).toFixed(1) : 0;
}});
new Chart(document.getElementById('cacheChart'),{{
  type:'line',
  data:{{ labels:sorted.map(r=>'#'+r.id),
          datasets:[{{label:'캐시 적중률 %',data:cacheRates,
                      borderColor:'#b794f4',tension:.3,fill:true,
                      backgroundColor:'rgba(183,148,244,.1)'}}] }},
  options:{{ plugins:{{legend:{{labels:{{color:'#a0aec0'}}}}}},
             scales:{{ y:{{min:0,max:100,ticks:{{color:'#718096'}}, grid:{{color:'#2d3748'}}}},
                       x:{{ticks:{{color:'#718096'}}, grid:{{color:'#2d3748'}} }} }} }}
}});

// ── 품질 지표 트렌드 ─────────────────────────────────────
new Chart(document.getElementById('qualityChart'),{{
  type:'line',
  data:{{ labels:sorted.map(r=>'#'+r.id),
          datasets:[
            {{label:'컴파일 성공',data:sorted.map(r=>r.compile_ok?1:0),
              borderColor:'#68d391',stepped:true,fill:false}},
            {{label:'테스트 통과율',data:sorted.map(r=>r.test_pass_rate!=null?r.test_pass_rate:null),
              borderColor:'#63b3ed',tension:.3,fill:false,spanGaps:true}},
            {{label:'평점/5',data:sorted.map(r=>r.rating!=null?r.rating/5:null),
              borderColor:'#f6e05e',tension:.3,fill:false,spanGaps:true}},
          ] }},
  options:{{ plugins:{{legend:{{labels:{{color:'#a0aec0'}}}}}},
             scales:{{ y:{{min:0,max:1,ticks:{{color:'#718096'}}, grid:{{color:'#2d3748'}}}},
                       x:{{ticks:{{color:'#718096'}}, grid:{{color:'#2d3748'}} }} }} }}
}});

// ── 상세 테이블 ──────────────────────────────────────────
const tbody = document.getElementById('runsBody');
// CLAUDE.md 해시 변경 기준으로 구분선 표시
let prevHash = null;
let groupIdx = 0;
[...RUNS].reverse().forEach(r => {{
  if (r.claude_md_hash && r.claude_md_hash !== prevHash) {{
    if (prevHash !== null) {{
      groupIdx++;
      const sep = document.createElement('tr');
      sep.innerHTML = `<td colspan="13">
        <div class="section-label">CLAUDE.md 변경 → 그룹 ${{groupIdx+1}} 시작
          (${{r.claude_md_hash.slice(0,8)}})</div></td>`;
      tbody.appendChild(sep);
    }}
    prevHash = r.claude_md_hash;
  }}

  const compBadge = r.compile_ok
    ? '<span class="badge ok">OK</span>'
    : '<span class="badge fail">FAIL</span>';
  const testBadge = r.test_pass_rate != null
    ? `<span class="badge ${{r.test_pass_rate>=0.9?'ok':'fail'}}">${{(r.test_pass_rate*100).toFixed(0)}}%</span>`
    : '<span class="badge na">—</span>';

  const notesShort = (r.notes||'').split('\\n').slice(0,3).join(' / ').slice(0,80);

  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>#${{r.id}}</td>
    <td>${{(r.recorded_at||'').slice(0,16)}}</td>
    <td><span class="tag">${{r.runner||''}}</span></td>
    <td style="font-size:11px;color:#90cdf4">${{(r.branch||'').replace('feat/','').replace('fix/','')}}</td>
    <td>${{fmt(r.turn_count)}}</td>
    <td>${{fmt(r.output_tokens)}}</td>
    <td>${{fmt(r.cache_read)}}</td>
    <td>$${{(r.billing_usd||0).toFixed(4)}}</td>
    <td>${{compBadge}}</td>
    <td>${{testBadge}}</td>
    <td class="diff-line">+${{r.added_lines||0}} / -${{r.deleted_lines||0}}</td>
    <td>
      <span class="stars">${{stars(r.rating)}}</span>
      <div>
        ${{[1,2,3,4,5].map(n=>`<button class="rating-btn" onclick="rate(${{r.id}},${{n}})">${{n}}</button>`).join('')}}
      </div>
    </td>
    <td style="font-size:11px;color:#718096;max-width:200px">${{notesShort}}</td>
  `;
  tbody.appendChild(tr);
}});

// ── 평점 입력 ────────────────────────────────────────────
async function rate(runId, score) {{
  await fetch(`/rate/${{runId}}/${{score}}`).catch(()=>{{}});
  // 서버 없을 때 — Python 스크립트 직접 호출 fallback은 CLI에서 처리
  alert(`run #${{runId}} 평점 ${{score}} 저장 → 터미널에서:\\nexp rate ${{runId}} ${{score}}`);
}}
</script>
</body>
</html>"""

    OUT.write_text(html, encoding="utf-8")
    print(f"리포트 생성: {OUT}")
    webbrowser.open(f"file://{OUT.resolve()}")


if __name__ == "__main__":
    build_report()
