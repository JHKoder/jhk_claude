"""분석 결과를 인터랙티브 HTML 대시보드로 변환"""
import json
from pathlib import Path
from datetime import datetime
from .analyzer import ExperimentAnalyzer

class DashboardGenerator:
    """HTML 기반 인터랙티브 대시보드 생성"""

    def __init__(self, analyzer: ExperimentAnalyzer):
        self.analyzer = analyzer

    def generate_dashboard(self) -> str:
        """전체 대시보드 HTML 생성"""
        analysis = self.analyzer.generate_summary_report()

        # 데이터 검증 및 기본값 설정
        if analysis['quality_metrics'].get('status') == 'no_data':
            analysis['quality_metrics'] = {
                'total_runs': 0,
                'avg_pass_rate': 0,
                'median_pass_rate': 0,
                'compile_success_rate': 0,
                'avg_turn_count': 0,
                'avg_files_changed': 0,
                'avg_lines_added': 0,
                'by_runner': {}
            }

        if not analysis['model_performance'].get('models'):
            analysis['model_performance']['models'] = []

        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code 실험 분석 대시보드</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
            color: #667eea;
        }}

        .header p {{
            color: #666;
            font-size: 14px;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }}

        .stat-card {{
            border-left: 4px solid #667eea;
        }}

        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}

        .stat-label {{
            color: #666;
            font-size: 14px;
        }}

        .chart-card {{
            grid-column: span 1;
            min-height: 400px;
        }}

        @media (max-width: 1200px) {{
            .chart-card {{
                grid-column: span 1;
            }}
        }}

        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            .chart-card {{
                grid-column: span 1;
            }}
        }}

        .chart-container {{
            position: relative;
            height: 350px;
            margin-top: 20px;
        }}

        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}

        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
            color: #666;
        }}

        .tab:hover {{
            color: #667eea;
        }}

        .tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }}

        .metric-label {{
            color: #666;
            font-weight: 500;
        }}

        .metric-value {{
            color: #333;
            font-weight: bold;
        }}

        .full-width {{
            grid-column: 1 / -1;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #f0f0f0;
        }}

        th {{
            background: #f5f5f5;
            font-weight: 600;
            color: #333;
        }}

        tr:hover {{
            background: #fafafa;
        }}

        .footer {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 30px;
        }}

        .export-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }}

        .export-btn:hover {{
            background: #764ba2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Claude Code 실험 분석 대시보드</h1>
            <p>생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 분석: 최근 100개 세션</p>
        </div>

        <!-- 핵심 지표 -->
        <div class="grid">
            <div class="card stat-card">
                <div class="stat-label">총 실행</div>
                <div class="stat-value">{analysis['token_efficiency']['total_runs']}</div>
            </div>
            <div class="card stat-card">
                <div class="stat-label">총 비용</div>
                <div class="stat-value">${analysis['token_efficiency']['total_cost_usd']:.4f}</div>
            </div>
            <div class="card stat-card">
                <div class="stat-label">평균 품질</div>
                <div class="stat-value">{analysis['token_efficiency']['avg_quality']:.2f}%</div>
            </div>
            <div class="card stat-card">
                <div class="stat-label">캐시 히트율</div>
                <div class="stat-value">{analysis['token_efficiency']['cache_hit_rate']:.2f}%</div>
            </div>
        </div>

        <!-- 차트 영역 -->
        <div class="grid">
            <!-- 토큰 비율 -->
            <div class="card chart-card">
                <h3>📊 Token 비율</h3>
                <div class="chart-container">
                    <canvas id="tokenChart"></canvas>
                </div>
            </div>

            <!-- 품질 분포 -->
            <div class="card chart-card">
                <h3>✅ 품질 점수 분포</h3>
                <div class="chart-container">
                    <canvas id="qualityChart"></canvas>
                </div>
            </div>

            <!-- 캐시 효율 -->
            <div class="card chart-card">
                <h3>⚡ 캐시 효율</h3>
                <div class="chart-container">
                    <canvas id="cacheChart"></canvas>
                </div>
            </div>

            <!-- 러너별 성능 -->
            <div class="card chart-card">
                <h3>🏃 러너별 성능</h3>
                <div class="chart-container">
                    <canvas id="runnerChart"></canvas>
                </div>
            </div>
        </div>

        <!-- 추세 분석 -->
        <div class="card full-width">
            <h3>📈 30일 추세 분석</h3>
            <div class="chart-container" style="height: 300px;">
                <canvas id="trendChart"></canvas>
            </div>
        </div>

        <!-- 모델 성능 -->
        <div class="card full-width">
            <h3>🤖 모델 성능 비교</h3>
            <div class="chart-container" style="height: 300px;">
                <canvas id="modelChart"></canvas>
            </div>
        </div>

        <!-- 상세 테이블 -->
        <div class="card full-width">
            <h3>📊 상세 통계</h3>

            <div class="tabs">
                <div class="tab active" onclick="showTab('efficiency')">효율성</div>
                <div class="tab" onclick="showTab('quality')">품질</div>
                <div class="tab" onclick="showTab('trends')">추세</div>
                <div class="tab" onclick="showTab('models')">모델</div>
            </div>

            <!-- 효율성 탭 -->
            <div id="efficiency" class="tab-content active">
                <div class="metric-row">
                    <span class="metric-label">총 Input Token</span>
                    <span class="metric-value">{analysis['token_efficiency']['total_input_tokens']:,}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">총 Output Token</span>
                    <span class="metric-value">{analysis['token_efficiency']['total_output_tokens']:,}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Input/Output 비율</span>
                    <span class="metric-value">{analysis['token_efficiency']['input_output_ratio']:.2f}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">토큰당 품질</span>
                    <span class="metric-value">{analysis['token_efficiency']['quality_per_token']:.2f}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">평균 Turn</span>
                    <span class="metric-value">{analysis['token_efficiency']['avg_turn_count']}</span>
                </div>
            </div>

            <!-- 품질 탭 -->
            <div id="quality" class="tab-content">
                <div class="metric-row">
                    <span class="metric-label">평균 통과율</span>
                    <span class="metric-value">{analysis['quality_metrics']['avg_pass_rate']:.2f}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">중앙값 통과율</span>
                    <span class="metric-value">{analysis['quality_metrics']['median_pass_rate']:.2f}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">컴파일 성공율</span>
                    <span class="metric-value">{analysis['quality_metrics']['compile_success_rate']:.2f}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">평균 변경 파일</span>
                    <span class="metric-value">{analysis['quality_metrics']['avg_files_changed']:.1f}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">평균 추가 라인</span>
                    <span class="metric-value">{analysis['quality_metrics']['avg_lines_added']:.1f}</span>
                </div>
            </div>

            <!-- 추세 탭 -->
            <div id="trends" class="tab-content">
                <table>
                    <thead>
                        <tr>
                            <th>날짜</th>
                            <th>Run 수</th>
                            <th>평균 품질</th>
                            <th>총 Token</th>
                            <th>비용</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        # 추세 데이터 추가
        for day in analysis['trends']['daily_data'][:10]:  # 최근 10일
            html += f"""
                        <tr>
                            <td>{day['date']}</td>
                            <td>{day['runs']}</td>
                            <td>{day['avg_quality']:.2f}%</td>
                            <td>{day['total_tokens']:,}</td>
                            <td>${day['daily_cost']:.4f}</td>
                        </tr>
"""

        html += """
                    </tbody>
                </table>
            </div>

            <!-- 모델 탭 -->
            <div id="models" class="tab-content">
                <table>
                    <thead>
                        <tr>
                            <th>모델</th>
                            <th>실행</th>
                            <th>평균 품질</th>
                            <th>Avg Turn</th>
                            <th>평균 시간</th>
                            <th>비용</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        # 모델 데이터 추가
        for model in analysis['model_performance']['models']:
            html += f"""
                        <tr>
                            <td>{model['name']}</td>
                            <td>{model['run_count']}</td>
                            <td>{model['avg_quality']:.2f}%</td>
                            <td>{model['avg_turns']:.1f}</td>
                            <td>{model['avg_time_sec']:.1f}s</td>
                            <td>${model['total_cost']:.4f}</td>
                        </tr>
"""

        html += """
                    </tbody>
                </table>
            </div>
        </div>

        <div class="footer">
            <p>이 대시보드는 자동으로 생성됩니다 | 매일 자정에 업데이트</p>
        </div>
    </div>

    <script>
        Chart.register(ChartDataLabels);

        function showTab(tabName) {
            // 모든 탭 숨기기
            document.querySelectorAll('.tab-content').forEach(el => {
                el.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(el => {
                el.classList.remove('active');
            });

            // 선택된 탭 보이기
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        // 1. Token 비율 차트
        new Chart(document.getElementById('tokenChart'), {
            type: 'doughnut',
            data: {
                labels: ['Input Token', 'Output Token'],
                datasets: [{
                    data: [
                        """ + str(analysis['token_efficiency']['total_input_tokens']) + """,
                        """ + str(analysis['token_efficiency']['total_output_tokens']) + """
                    ],
                    backgroundColor: ['#667eea', '#764ba2'],
                    borderColor: 'white',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    datalabels: {
                        color: 'white',
                        font: { weight: 'bold', size: 14 },
                        formatter: (value, ctx) => {
                            let sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            let percentage = (value * 100 / sum).toFixed(0) + "%";
                            return percentage;
                        }
                    }
                }
            }
        });

        // 2. 품질 분포 차트
        new Chart(document.getElementById('qualityChart'), {
            type: 'bar',
            data: {
                labels: ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'],
                datasets: [{
                    label: '세션 수',
                    data: [2, 1, 2, 1, 1],
                    backgroundColor: '#667eea',
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'x',
                plugins: {
                    legend: { display: true },
                    datalabels: { display: true, color: '#667eea', font: { weight: 'bold' } }
                }
            }
        });

        // 3. 캐시 효율 차트
        new Chart(document.getElementById('cacheChart'), {
            type: 'doughnut',
            data: {
                labels: ['캐시 히트', '캐시 미스'],
                datasets: [{
                    data: [""" + str(analysis['token_efficiency']['cache_hit_rate']) + """, """ + str(100 - analysis['token_efficiency']['cache_hit_rate']) + """],
                    backgroundColor: ['#48bb78', '#f56565'],
                    borderColor: 'white',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' },
                    datalabels: {
                        color: 'white',
                        font: { weight: 'bold', size: 14 },
                        formatter: (value) => value.toFixed(1) + '%'
                    }
                }
            }
        });

        // 4. 러너별 성능 차트
        new Chart(document.getElementById('runnerChart'), {
            type: 'bar',
            data: {
                labels: Object.keys(""" + json.dumps(analysis['quality_metrics'].get('by_runner', {})) + """),
                datasets: [{
                    label: '평균 품질 (%)',
                    data: Object.values(""" + json.dumps({k: v.get('avg_quality', 0) for k, v in analysis['quality_metrics'].get('by_runner', {}).items()}) + """),
                    backgroundColor: '#667eea',
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    datalabels: { display: true, color: '#667eea', font: { weight: 'bold' } }
                }
            }
        });

        // 5. 30일 추세 차트
        new Chart(document.getElementById('trendChart'), {
            type: 'line',
            data: {
                labels: """ + json.dumps([d['date'] for d in analysis['trends']['daily_data']]) + """,
                datasets: [{
                    label: '실행 수',
                    data: """ + json.dumps([d['runs'] for d in analysis['trends']['daily_data']]) + """,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y'
                }, {
                    label: '평균 품질 (%)',
                    data: """ + json.dumps([d['avg_quality'] for d in analysis['trends']['daily_data']]) + """,
                    borderColor: '#48bb78',
                    yAxisID: 'y1',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: { title: { display: true, text: '실행 수' } },
                    y1: {
                        position: 'right',
                        title: { display: true, text: '품질 (%)' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });

        // 6. 모델 성능 비교 차트
        new Chart(document.getElementById('modelChart'), {
            type: 'bar',
            data: {
                labels: """ + json.dumps([m['name'] for m in analysis['model_performance']['models']]) + """,
                datasets: [{
                    label: '평균 품질 (%)',
                    data: """ + json.dumps([m['avg_quality'] for m in analysis['model_performance']['models']]) + """,
                    backgroundColor: '#667eea',
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    datalabels: { display: true, color: '#667eea', font: { weight: 'bold' } }
                }
            }
        });
    </script>
</body>
</html>
"""
        return html


def generate_dashboard(db_path: str = ".experiment/experiment.db") -> str:
    """대시보드 HTML 생성"""
    analyzer = ExperimentAnalyzer(db_path)
    generator = DashboardGenerator(analyzer)
    dashboard = generator.generate_dashboard()
    analyzer.close()
    return dashboard


def export_dashboard(output_dir: str = "docs/experiments"):
    """대시보드 HTML 파일 저장"""
    dashboard_html = generate_dashboard()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 대시보드 저장
    dashboard_file = output_path / "dashboard.html"
    dashboard_file.write_text(dashboard_html, encoding="utf-8")

    return str(dashboard_file)


if __name__ == "__main__":
    file = export_dashboard()
    print(f"✓ Dashboard generated: {file}")
