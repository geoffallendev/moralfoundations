"""
HTML Report Generator for Moral Foundations Analysis
Generates interactive HTML visualizations from JSON results
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd


class HTMLReportGenerator:
    """Generates HTML reports from moral foundations analysis results"""

    def __init__(self, json_path: str, summary_path: str = None):
        self.json_path = json_path
        self.summary_path = summary_path
        self.results = []
        self.df = None

        self._load_data()

    def _load_data(self):
        """Load JSON results"""
        with open(self.json_path, 'r') as f:
            self.results = json.load(f)

        self.df = pd.DataFrame(self.results)
        self.valid_df = self.df[self.df['extracted_value'] >= 0]

    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate statistics for visualization"""
        stats = {
            'llms': sorted(self.df['llm'].unique()),
            'foundations': sorted(self.valid_df['moral_foundation'].unique()),
            'by_llm_foundation': {},
            'total_by_foundation': {},
        }

        # Sum by LLM and foundation
        for llm in stats['llms']:
            llm_df = self.valid_df[self.valid_df['llm'] == llm]
            stats['by_llm_foundation'][llm] = {}

            for foundation in stats['foundations']:
                foundation_df = llm_df[llm_df['moral_foundation'] == foundation]
                sum_score = int(foundation_df['extracted_value'].sum())
                stats['by_llm_foundation'][llm][foundation] = sum_score

        # Total by foundation across all LLMs
        for foundation in stats['foundations']:
            foundation_df = self.valid_df[self.valid_df['moral_foundation'] == foundation]
            sum_score = int(foundation_df['extracted_value'].sum())
            stats['total_by_foundation'][foundation] = sum_score

        return stats

    def generate_html(self, output_path: str = None) -> str:
        """Generate HTML report"""
        if output_path is None:
            output_path = self.json_path.replace('.json', '.html')

        stats = self._calculate_statistics()

        html_content = self._build_html(stats)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ Generated HTML report: {output_path}")
        return output_path

    def _build_html(self, stats: Dict[str, Any]) -> str:
        """Build complete HTML document"""

        # Prepare data for Chart.js
        foundations_short = [f.replace('Fairness-Reciprocity', 'Fairness')
                            .replace('Purity-Sancity', 'Purity')
                            .replace('Harm-Care', 'Harm') for f in stats['foundations']]

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moral Foundations Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 50px;
        }}

        .section h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}

        .stat-card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .stat-card .value {{
            font-size: 2.5em;
            font-weight: 700;
        }}

        .chart-container {{
            position: relative;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);
        }}

        .chart-wrapper {{
            position: relative;
            height: 400px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}

        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }}

        tbody tr:hover {{
            background: #f8f9fa;
        }}

        tbody tr:last-child td {{
            border-bottom: none;
        }}

        .llm-badge {{
            display: inline-block;
            padding: 5px 12px;
            background: #667eea;
            color: white;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .score-cell {{
            font-weight: 600;
            color: #667eea;
            font-size: 1.1em;
        }}

        .foundation-label {{
            font-weight: 500;
            color: #495057;
        }}

        footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }}

        .grid-2col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}

        /* Accordion Styles */
        .responses-container {{
            margin-top: 20px;
        }}

        .accordion-item {{
            margin-bottom: 15px;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}

        .accordion-header {{
            width: 100%;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: none;
            padding: 20px;
            text-align: left;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }}

        .accordion-header:hover {{
            background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        }}

        .accordion-title {{
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}

        .question-badge {{
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .foundation-tag {{
            background: #764ba2;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .part-tag {{
            background: #ed64a6;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .question-text {{
            color: #495057;
            font-size: 0.95em;
            line-height: 1.5;
            margin-bottom: 5px;
        }}

        .accordion-icon {{
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            transition: transform 0.3s ease;
            font-size: 1.2em;
            color: #667eea;
        }}

        .accordion-icon.rotated {{
            transform: translateY(-50%) rotate(180deg);
        }}

        .accordion-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            background: white;
        }}

        .accordion-content.active {{
            max-height: 10000px;
            padding: 20px;
            border-top: 2px solid #e9ecef;
        }}

        .full-question {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }}

        .responses-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 15px;
        }}

        .response-card {{
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 15px;
            background: #f8f9fa;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .response-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .response-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e9ecef;
        }}

        .value-badge {{
            padding: 5px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .value-badge.valid-value {{
            background: #d4edda;
            color: #155724;
        }}

        .value-badge.invalid-value {{
            background: #f8d7da;
            color: #721c24;
        }}

        .response-body {{
            margin-bottom: 12px;
        }}

        .response-text {{
            background: white;
            padding: 12px;
            border-radius: 6px;
            margin-top: 8px;
            font-size: 0.9em;
            line-height: 1.6;
            color: #495057;
            border-left: 3px solid #667eea;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .response-footer {{
            text-align: right;
            color: #6c757d;
            font-size: 0.8em;
        }}

        @media (max-width: 768px) {{
            .grid-2col {{
                grid-template-columns: 1fr;
            }}

            header h1 {{
                font-size: 1.8em;
            }}

            .chart-wrapper {{
                height: 300px;
            }}

            .responses-grid {{
                grid-template-columns: 1fr;
            }}

            .accordion-title {{
                flex-direction: column;
                gap: 5px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Moral Foundations Analysis Report</h1>
            <p>LLM Comparative Analysis Using MFQ-30 Questionnaire</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </header>

        <div class="content">
            <!-- Summary Statistics -->
            <section class="section">
                <h2>Summary Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Total Responses</h3>
                        <div class="value">{len(self.results)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>LLMs Tested</h3>
                        <div class="value">{len(stats['llms'])}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Questions Analyzed</h3>
                        <div class="value">{self.df['question'].nunique()}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Valid Responses</h3>
                        <div class="value">{len(self.valid_df)}</div>
                    </div>
                </div>
            </section>

            <!-- Charts Section -->
            <section class="section">
                <h2>Visual Analysis</h2>

                <div class="chart-container">
                    <h3 style="margin-bottom: 20px; color: #495057;">Sum of Scores by LLM and Moral Foundation</h3>
                    <div class="chart-wrapper">
                        <canvas id="foundationChart"></canvas>
                    </div>
                </div>
            </section>

            <!-- Detailed Tables -->
            <section class="section">
                <h2>Detailed Scores by LLM and Moral Foundation</h2>
                {self._build_foundation_table(stats)}
            </section>

            <!-- Detailed Responses Section -->
            <section class="section">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2 style="margin-bottom: 0;">Detailed LLM Responses by Question</h2>
                    <div style="display: flex; gap: 10px;">
                        <button onclick="expandAll()" style="padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9em;">
                            Expand All
                        </button>
                        <button onclick="collapseAll()" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9em;">
                            Collapse All
                        </button>
                    </div>
                </div>
                {self._build_detailed_responses()}
            </section>
        </div>

        <footer>
            <p>Generated from: {os.path.basename(self.json_path)}</p>
            <p style="margin-top: 5px;">Moral Foundations Theory Analysis Tool</p>
        </footer>
    </div>

    <script>
        // Chart.js default settings
        Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        Chart.defaults.color = '#495057';

        // Color palette
        const colors = [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(237, 100, 166, 0.8)',
            'rgba(255, 154, 158, 0.8)',
            'rgba(250, 208, 196, 0.8)',
        ];

        const borderColors = [
            'rgba(102, 126, 234, 1)',
            'rgba(118, 75, 162, 1)',
            'rgba(237, 100, 166, 1)',
            'rgba(255, 154, 158, 1)',
            'rgba(250, 208, 196, 1)',
        ];

        // Data preparation
        const llms = {json.dumps(stats['llms'])};
        const foundations = {json.dumps(foundations_short)};
        const foundationsFull = {json.dumps(stats['foundations'])};
        const byLlmFoundation = {json.dumps(stats['by_llm_foundation'])};

        // Foundation Chart Data
        const foundationData = {{
            labels: foundations,
            datasets: llms.map((llm, idx) => ({{
                label: llm,
                data: foundationsFull.map(f => byLlmFoundation[llm][f] || 0),
                backgroundColor: colors[idx % colors.length],
                borderColor: borderColors[idx % borderColors.length],
                borderWidth: 2
            }}))
        }};

        // Create chart
        new Chart(document.getElementById('foundationChart'), {{
            type: 'bar',
            data: foundationData,
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                    title: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Sum of Scores'
                        }}
                    }}
                }}
            }}
        }});

        // Accordion toggle function
        function toggleAccordion(id) {{
            const content = document.getElementById('content-' + id);
            const icon = document.getElementById('icon-' + id);

            if (content.classList.contains('active')) {{
                content.classList.remove('active');
                icon.classList.remove('rotated');
            }} else {{
                content.classList.add('active');
                icon.classList.add('rotated');
            }}
        }}

        // Add expand/collapse all functionality
        function expandAll() {{
            document.querySelectorAll('.accordion-content').forEach(content => {{
                content.classList.add('active');
            }});
            document.querySelectorAll('.accordion-icon').forEach(icon => {{
                icon.classList.add('rotated');
            }});
        }}

        function collapseAll() {{
            document.querySelectorAll('.accordion-content').forEach(content => {{
                content.classList.remove('active');
            }});
            document.querySelectorAll('.accordion-icon').forEach(icon => {{
                icon.classList.remove('rotated');
            }});
        }}
    </script>
</body>
</html>
"""
        return html

    def _build_foundation_table(self, stats: Dict[str, Any]) -> str:
        """Build HTML table for foundation scores"""
        html = '<table><thead><tr><th>LLM</th>'

        for foundation in stats['foundations']:
            html += f'<th>{foundation}</th>'

        html += '</tr></thead><tbody>'

        for llm in stats['llms']:
            html += f'<tr><td><span class="llm-badge">{llm}</span></td>'

            for foundation in stats['foundations']:
                score = stats['by_llm_foundation'][llm].get(foundation, 0)
                html += f'<td class="score-cell">{score}</td>'

            html += '</tr>'

        html += '</tbody></table>'
        return html

    def _build_detailed_responses(self) -> str:
        """Build HTML for detailed LLM responses organized by question"""
        html = '<div class="responses-container">'

        # Group responses by question
        questions_dict = {}
        for result in self.results:
            q = result['question']
            if q not in questions_dict:
                questions_dict[q] = {
                    'moral_foundation': result['moral_foundation'],
                    'part': result['part'],
                    'responses': []
                }
            questions_dict[q]['responses'].append(result)

        # Build accordion for each question
        for idx, (question, data) in enumerate(questions_dict.items()):
            question_short = question[:100] + '...' if len(question) > 100 else question

            html += f'''
            <div class="accordion-item">
                <button class="accordion-header" onclick="toggleAccordion('{idx}')">
                    <div class="accordion-title">
                        <span class="question-badge">Question {idx + 1}</span>
                        <span class="foundation-tag">{data['moral_foundation']}</span>
                        <span class="part-tag">Part {data['part']}</span>
                    </div>
                    <div class="question-text">{question_short}</div>
                    <span class="accordion-icon" id="icon-{idx}">▼</span>
                </button>
                <div class="accordion-content" id="content-{idx}">
                    <div class="full-question">
                        <strong>Full Question:</strong><br>
                        {question}
                    </div>
                    <div class="responses-grid">
            '''

            # Add each LLM's response
            for response in sorted(data['responses'], key=lambda x: x['llm']):
                extracted_val = response['extracted_value']
                val_class = 'valid-value' if extracted_val >= 0 else 'invalid-value'

                html += f'''
                    <div class="response-card">
                        <div class="response-header">
                            <span class="llm-badge">{response['llm']}</span>
                            <span class="value-badge {val_class}">
                                Value: {extracted_val if extracted_val >= 0 else 'N/A'}
                            </span>
                        </div>
                        <div class="response-body">
                            <strong>Response:</strong><br>
                            <div class="response-text">{response['response']}</div>
                        </div>
                        <div class="response-footer">
                            <small>{response['timestamp']}</small>
                        </div>
                    </div>
                '''

            html += '''
                    </div>
                </div>
            </div>
            '''

        html += '</div>'
        return html


def main():
    """Standalone HTML generator"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_html_report.py <json_results_file> [summary_file]")
        print("\nExample:")
        print("  python generate_html_report.py results/moral_foundations_results_20240101_120000.json")
        sys.exit(1)

    json_path = sys.argv[1]
    summary_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(json_path):
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    generator = HTMLReportGenerator(json_path, summary_path)
    output_path = generator.generate_html()

    print(f"\nHTML report generated successfully!")
    print(f"Open in browser: file://{os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
