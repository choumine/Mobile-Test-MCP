# tools.py
from .common import app

import json
import datetime
import os
from typing import Dict, List, Any


class TestReportGenerator:
    def __init__(self):
        self.status_icons = {
            'passed': '✅',
            'failed': '❌',
            'blocked': '🚫',
            'skipped': '⏭️'
        }
        
        self.status_text = {
            'passed': 'Passed',
            'failed': 'Failed',
            'blocked': 'Blocked',
            'skipped': 'Skipped'
        }
        
        self.status_colors = {
            'passed': '#28a745',
            'failed': '#dc3545',
            'blocked': '#ffc107',
            'skipped': '#6c757d'
        }

    def parse_json_input(self, json_str: str) -> Dict[str, Any]:
        """Parse JSON input string"""
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON format error: {e}")

    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate data format"""
        required_fields = ['project_info', 'test_cases']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate project info
        project_info = data['project_info']
        project_required = ['name', 'version', 'tester']
        for field in project_required:
            if field not in project_info:
                raise ValueError(f"Project info missing required field: {field}")
        
        # Validate test cases
        if not isinstance(data['test_cases'], list) or len(data['test_cases']) == 0:
            raise ValueError("Test cases must be a non-empty array")
        
        for i, case in enumerate(data['test_cases']):
            case_required = ['name', 'status']
            for field in case_required:
                if field not in case:
                    raise ValueError(f"Test case {i+1} missing required field: {field}")
            
            if case['status'] not in self.status_icons:
                raise ValueError(f"Test case {i+1} has invalid status: {case['status']}")

    def calculate_statistics(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate test statistics"""
        stats = {
            'total': len(test_cases),
            'passed': 0,
            'failed': 0,
            'blocked': 0,
            'skipped': 0
        }
        
        for case in test_cases:
            status = case['status']
            if status in stats:
                stats[status] += 1
        
        # Calculate pass rate
        pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        stats['pass_rate'] = round(pass_rate, 1)
        
        return stats

    def generate_pie_chart_css(self, stats: Dict[str, Any]) -> str:
        """Generate CSS for pie chart"""
        total = stats['total']
        if total == 0:
            return ""
        
        # Calculate angles for each status
        passed_deg = (stats['passed'] / total) * 360
        failed_deg = (stats['failed'] / total) * 360
        blocked_deg = (stats['blocked'] / total) * 360
        
        # Cumulative angles
        passed_end = passed_deg
        failed_end = passed_end + failed_deg
        blocked_end = failed_end + blocked_deg
        
        css = f"""
        background: conic-gradient(
            {self.status_colors['passed']} 0deg {passed_end}deg,
            {self.status_colors['failed']} {passed_end}deg {failed_end}deg,
            {self.status_colors['blocked']} {failed_end}deg {blocked_end}deg,
            {self.status_colors['skipped']} {blocked_end}deg 360deg
        );
        """
        
        return css

    def generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML test report"""
        project_info = data['project_info']
        test_cases = data['test_cases']
        stats = self.calculate_statistics(test_cases)
        
        # Get test date
        test_date = project_info.get('test_date', datetime.datetime.now().strftime('%Y-%m-%d'))
        
        # Generate test case table rows
        test_case_rows = ""
        for i, case in enumerate(test_cases, 1):
            status = case['status']
            status_class = f"status-{status}"
            status_display = f"{self.status_icons[status]} {self.status_text[status]}"
            
            # Handle screenshot info
            pre_screenshot = case.get('pre_screenshot', '')
            post_screenshot = case.get('post_screenshot', '')
            
            screenshot_html = ""
            if pre_screenshot or post_screenshot:
                screenshot_html += '<div class="screenshot-container">'
                if pre_screenshot:
                    screenshot_html += f'''
                    <div class="screenshot-item">
                        <div class="screenshot-label">Before</div>
                        <a href="{pre_screenshot}" target="_blank">
                            <img src="{pre_screenshot}" alt="Before screenshot" class="screenshot-thumb">
                        </a>
                    </div>'''
                if post_screenshot:
                    screenshot_html += f'''
                    <div class="screenshot-item">
                        <div class="screenshot-label">After</div>
                        <a href="{post_screenshot}" target="_blank">
                            <img src="{post_screenshot}" alt="After screenshot" class="screenshot-thumb">
                        </a>
                    </div>'''
                screenshot_html += '</div>'
            
            test_case_rows += f"""
                <tr>
                    <td>{i}</td>
                    <td>{case['name']}</td>
                    <td>{case.get('description', 'No description')}</td>
                    <td class="{status_class}">{status_display}</td>
                    <td>{case.get('remark', 'No remarks')}</td>
                    <td>{screenshot_html}</td>
                </tr>
            """
        
        # Generate pie chart CSS
        pie_chart_css = self.generate_pie_chart_css(stats)
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_info['name']} - Test Report</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .report-container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .report-header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .report-header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5rem;
        }}
        .report-content {{
            padding: 40px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-top: 4px solid #007bff;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #495057;
        }}
        .summary-card .number {{
            font-size: 2rem;
            font-weight: bold;
            color: #007bff;
        }}
        .pass-rate {{
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
        }}
        .table-container {{
            overflow-x: auto;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        th {{
            background: #f8f9fa;
            font-weight: bold;
            color: #495057;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .status-passed {{ color: #28a745; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .status-blocked {{ color: #ffc107; font-weight: bold; }}
        .status-skipped {{ color: #6c757d; font-weight: bold; }}
        .project-info {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #2196f3;
        }}
        .project-info h2 {{
            margin: 0 0 15px 0;
            color: #1976d2;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 5px;
        }}
        .info-label {{
            font-weight: bold;
            color: #666;
            margin-bottom: 5px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .pie-chart {{
            width: 200px;
            height: 200px;
            margin: 0 auto;
            border-radius: 50%;
            {pie_chart_css}
            position: relative;
        }}
        .pie-chart::after {{
            content: '{stats["pass_rate"]}%';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: bold;
            color: #333;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 0.9rem;
        }}
        /* Screenshot related styles */
        .screenshot-container {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .screenshot-item {{
            text-align: center;
        }}
        .screenshot-label {{
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 5px;
        }}
        .screenshot-thumb {{
            width: 80px;
            height: 120px;
            object-fit: cover;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .screenshot-thumb:hover {{
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        @media print {{
            body {{ padding: 0; background: white; }}
            .report-container {{ box-shadow: none; }}
        }}
        @media (max-width: 768px) {{
            .screenshot-thumb {{
                width: 60px;
                height: 90px;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="report-header">
            <h1>🧪 Test Report</h1>
            <p>Automatically generated test execution report</p>
        </div>
        
        <div class="report-content">
            <div class="project-info">
                <h2>📋 Project Information</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Project Name</div>
                        <div>{project_info['name']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Version</div>
                        <div>{project_info['version']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Tester</div>
                        <div>{project_info['tester']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Test Date</div>
                        <div>{test_date}</div>
                    </div>
                </div>
            </div>

            <div class="chart-container">
                <h2>📊 Test Results Statistics</h2>
                <div class="pie-chart"></div>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: {self.status_colors['passed']};"></div>
                        <span>Passed ({stats['passed']})</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: {self.status_colors['failed']};"></div>
                        <span>Failed ({stats['failed']})</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: {self.status_colors['blocked']};"></div>
                        <span>Blocked ({stats['blocked']})</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: {self.status_colors['skipped']};"></div>
                        <span>Skipped ({stats['skipped']})</span>
                    </div>
                </div>
            </div>

            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Total Cases</h3>
                    <div class="number">{stats['total']}</div>
                </div>
                <div class="summary-card">
                    <h3>Passed</h3>
                    <div class="number" style="color: #28a745;">{stats['passed']}</div>
                </div>
                <div class="summary-card">
                    <h3>Failed</h3>
                    <div class="number" style="color: #dc3545;">{stats['failed']}</div>
                </div>
                <div class="summary-card pass-rate">
                    <h3>Pass Rate</h3>
                    <div class="number">{stats['pass_rate']}%</div>
                </div>
            </div>

            <div class="table-container">
                <h2>📝 Detailed Test Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Test Case Name</th>
                            <th>Description</th>
                            <th>Status</th>
                            <th>Remarks</th>
                            <th>Screenshots</th>
                        </tr>
                    </thead>
                    <tbody>
                        {test_case_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Test Report Generator v1.0</p>
        </div>
    </div>
</body>
</html>"""
        
        return html_template

    def save_report(self, html_content: str, output_file: str = None) -> str:
        """Save HTML report to file"""
        if output_file is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'test_report_{timestamp}.html'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file


@app.tool()
def tool_generate_report(json_input: str, output_file: str = None) -> str:
    """
    A convenience function to generate test reports from JSON strings
    
    Args:
        json_input (str): JSON formatted test data string
        output_file (str): Output file name, optional
    
    Example:
        {
            "project_info": {
                "name": "Project Name",
                "version": "1.0.0",
                "tester": "Tester Name"
            },
            "test_cases": [
                {
                "name": "Test Case 1",
                "status": "passed",
                "description": "Case description",
                "remark": "Remarks",
                "pre_screenshot": "screenshot_before.png",
                "post_screenshot": "screenshot_after.png"
                }
            ]
        }

    Returns:
        str: Output file path
    """
    generator = TestReportGenerator()
    
    # Parse and validate data
    data = generator.parse_json_input(json_input)
    generator.validate_data(data)
    
    # Generate HTML report
    html_content = generator.generate_html_report(data)
    
    # Save and return file path
    return generator.save_report(html_content, output_file)