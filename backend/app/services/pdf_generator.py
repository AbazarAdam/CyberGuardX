"""
CyberGuardX - Professional PDF Report Generator
Generates comprehensive security assessment reports in PDF format.
Uses only Python standard library + basic HTML-to-PDF approach.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class PDFReportGenerator:
    """
    Generates professional security assessment reports.
    Outputs an HTML report that can be viewed in browser or printed to PDF.
    """

    SEVERITY_COLORS = {
        "CRITICAL": "#ff003c",
        "HIGH": "#ff6600",
        "MEDIUM": "#ffaa00",
        "LOW": "#00ff9d",
        "MINIMAL": "#00f3ff",
        "UNKNOWN": "#888888"
    }

    GRADE_COLORS = {
        "A": "#00ff9d",
        "B": "#00f3ff",
        "C": "#ffaa00",
        "D": "#ff6600",
        "F": "#ff003c"
    }

    def generate_html_report(
        self,
        scan_data: Dict,
        vulnerability_analysis: Dict = None,
        owasp_data: Dict = None,
        risk_data: Dict = None
    ) -> str:
        """
        Generate a comprehensive HTML security report.
        
        Args:
            scan_data: Complete scan results
            vulnerability_analysis: Deep vulnerability analysis
            owasp_data: OWASP compliance assessment
            risk_data: Risk scoring data
            
        Returns:
            HTML string of the complete report
        """
        url = scan_data.get("url", "Unknown")
        timestamp = scan_data.get("scan_timestamp", datetime.utcnow().isoformat())
        overall_grade = scan_data.get("overall_grade", "N/A")
        risk_score = scan_data.get("risk_score", 0)
        risk_level = scan_data.get("risk_level", "UNKNOWN")

        vulns = vulnerability_analysis.get("vulnerabilities", []) if vulnerability_analysis else []
        severity_counts = vulnerability_analysis.get("severity_counts", {}) if vulnerability_analysis else {}
        scorecard = vulnerability_analysis.get("security_scorecard", {}) if vulnerability_analysis else {}
        compliance = vulnerability_analysis.get("compliance_summary", {}) if vulnerability_analysis else {}
        prioritization = vulnerability_analysis.get("risk_prioritization", {}) if vulnerability_analysis else {}
        waf = vulnerability_analysis.get("waf_detection", {}) if vulnerability_analysis else {}

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CyberGuardX Security Report - {url}</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: #0a0a1a;
        color: #e0e0e0;
        line-height: 1.6;
    }}
    .report-container {{
        max-width: 900px;
        margin: 0 auto;
        padding: 40px 30px;
    }}
    .report-header {{
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #0a0a2e 0%, #1a1a3e 100%);
        border: 1px solid #00f3ff33;
        border-radius: 12px;
        margin-bottom: 30px;
    }}
    .report-header h1 {{
        font-size: 28px;
        color: #00f3ff;
        margin-bottom: 8px;
    }}
    .report-header .subtitle {{
        color: #888;
        font-size: 14px;
    }}
    .report-header .target-url {{
        color: #ff00ff;
        font-size: 16px;
        margin: 12px 0;
        word-break: break-all;
    }}
    .grade-hero {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 40px;
        padding: 30px;
        background: #0d0d2b;
        border: 1px solid #00f3ff22;
        border-radius: 12px;
        margin-bottom: 30px;
    }}
    .grade-circle {{
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        font-weight: bold;
        border: 4px solid;
    }}
    .grade-A {{ border-color: #00ff9d; color: #00ff9d; }}
    .grade-B {{ border-color: #00f3ff; color: #00f3ff; }}
    .grade-C {{ border-color: #ffaa00; color: #ffaa00; }}
    .grade-D {{ border-color: #ff6600; color: #ff6600; }}
    .grade-F {{ border-color: #ff003c; color: #ff003c; }}
    .grade-metrics {{ text-align: left; }}
    .grade-metrics .metric {{
        margin: 8px 0;
        font-size: 15px;
    }}
    .metric-label {{ color: #888; }}
    .metric-value {{ font-weight: bold; }}
    .section {{
        background: #0d0d2b;
        border: 1px solid #ffffff11;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
    }}
    .section h2 {{
        color: #00f3ff;
        font-size: 20px;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #00f3ff22;
    }}
    .section h3 {{
        color: #ff00ff;
        font-size: 16px;
        margin: 16px 0 8px 0;
    }}
    .severity-badge {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        color: #000;
    }}
    .sev-CRITICAL {{ background: #ff003c; }}
    .sev-HIGH {{ background: #ff6600; }}
    .sev-MEDIUM {{ background: #ffaa00; }}
    .sev-LOW {{ background: #00ff9d; }}
    .vuln-card {{
        background: #1a1a3e;
        border: 1px solid #ffffff11;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }}
    .vuln-card .vuln-title {{
        font-size: 15px;
        font-weight: bold;
        color: #e0e0e0;
        margin-bottom: 8px;
    }}
    .vuln-card .vuln-meta {{
        font-size: 13px;
        color: #888;
        margin-bottom: 8px;
    }}
    .vuln-card .explanation {{
        font-size: 14px;
        color: #ccc;
        margin: 8px 0;
        padding: 8px 12px;
        border-left: 3px solid #00f3ff;
        background: #0a0a2e;
    }}
    .vuln-card .fix-code {{
        background: #0a0a1a;
        padding: 10px;
        border-radius: 6px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 12px;
        color: #00ff9d;
        overflow-x: auto;
        white-space: pre-wrap;
        margin-top: 8px;
    }}
    .compliance-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }}
    .compliance-item {{
        padding: 12px;
        border-radius: 8px;
        background: #1a1a3e;
    }}
    .compliance-item.compliant {{ border-left: 3px solid #00ff9d; }}
    .compliance-item.non-compliant {{ border-left: 3px solid #ff003c; }}
    .scorecard-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 12px;
    }}
    .scorecard-item {{
        text-align: center;
        padding: 16px;
        background: #1a1a3e;
        border-radius: 8px;
    }}
    .scorecard-item .sc-grade {{
        font-size: 32px;
        font-weight: bold;
    }}
    .scorecard-item .sc-label {{
        font-size: 12px;
        color: #888;
        margin-top: 4px;
    }}
    .scorecard-item .sc-score {{
        font-size: 14px;
        color: #ccc;
    }}
    .priority-section {{
        margin: 8px 0;
    }}
    .priority-item {{
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 6px;
        font-size: 14px;
    }}
    .priority-immediate {{ background: #ff003c22; border-left: 3px solid #ff003c; }}
    .priority-24h {{ background: #ff660022; border-left: 3px solid #ff6600; }}
    .priority-7d {{ background: #ffaa0022; border-left: 3px solid #ffaa00; }}
    .priority-30d {{ background: #00f3ff22; border-left: 3px solid #00f3ff; }}
    .severity-summary {{
        display: flex;
        gap: 16px;
        justify-content: center;
        margin: 16px 0;
    }}
    .severity-count {{
        text-align: center;
        padding: 12px 20px;
        border-radius: 8px;
    }}
    .severity-count .count {{
        font-size: 28px;
        font-weight: bold;
    }}
    .severity-count .label {{
        font-size: 12px;
        color: #888;
    }}
    .footer {{
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 12px;
        border-top: 1px solid #ffffff11;
        margin-top: 30px;
    }}
    @media print {{
        body {{ background: white; color: #333; }}
        .report-container {{ max-width: 100%; }}
        .section {{ break-inside: avoid; }}
    }}
</style>
</head>
<body>
<div class="report-container">
"""

        # Header
        html += f"""
    <div class="report-header">
        <h1>🛡️ CyberGuardX Security Assessment Report</h1>
        <p class="subtitle">Professional Website Security Analysis</p>
        <p class="target-url">{url}</p>
        <p class="subtitle">Generated: {timestamp} | Report Type: Comprehensive Assessment</p>
    </div>
"""

        # Grade hero
        grade_class = f"grade-{overall_grade[0]}" if overall_grade else "grade-F"
        html += f"""
    <div class="grade-hero">
        <div class="grade-circle {grade_class}">{overall_grade}</div>
        <div class="grade-metrics">
            <div class="metric"><span class="metric-label">Risk Score:</span> <span class="metric-value">{risk_score}/100</span></div>
            <div class="metric"><span class="metric-label">Risk Level:</span> <span class="metric-value">{risk_level}</span></div>
            <div class="metric"><span class="metric-label">Vulnerabilities:</span> <span class="metric-value">{len(vulns)}</span></div>
            <div class="metric"><span class="metric-label">WAF Status:</span> <span class="metric-value">{waf.get('protection_level', 'Unknown')}</span></div>
            <div class="metric"><span class="metric-label">HTTP Grade:</span> <span class="metric-value">{scan_data.get('http_grade', 'N/A')}</span></div>
            <div class="metric"><span class="metric-label">SSL Grade:</span> <span class="metric-value">{scan_data.get('ssl_grade', 'N/A')}</span></div>
        </div>
    </div>
"""

        # Executive Summary - Severity counts
        html += """
    <div class="section">
        <h2>📊 Executive Summary</h2>
        <div class="severity-summary">
"""
        for sev, color in [("critical", "#ff003c"), ("high", "#ff6600"), ("medium", "#ffaa00"), ("low", "#00ff9d")]:
            count = severity_counts.get(sev, 0)
            html += f"""
            <div class="severity-count" style="background: {color}22;">
                <div class="count" style="color: {color};">{count}</div>
                <div class="label">{sev.upper()}</div>
            </div>
"""
        html += """
        </div>
    </div>
"""

        # Security Scorecard
        if scorecard and scorecard.get("categories"):
            html += """
    <div class="section">
        <h2>📋 Security Scorecard</h2>
        <div class="scorecard-grid">
"""
            for cat_name, cat_data in scorecard["categories"].items():
                g = cat_data.get("grade", "?")
                gc = self.GRADE_COLORS.get(g, "#888")
                html += f"""
            <div class="scorecard-item">
                <div class="sc-grade" style="color: {gc};">{g}</div>
                <div class="sc-score">{cat_data.get('score', 0)}/100</div>
                <div class="sc-label">{cat_name}</div>
            </div>
"""
            html += """
        </div>
    </div>
"""

        # Risk Prioritization
        if prioritization:
            html += """
    <div class="section">
        <h2>⏱️ Remediation Priority</h2>
"""
            for timeline, css_class, label in [
                ("immediate", "priority-immediate", "🔴 IMMEDIATE"),
                ("within_24_hours", "priority-24h", "🟠 Within 24 Hours"),
                ("within_7_days", "priority-7d", "🟡 Within 7 Days"),
                ("within_30_days", "priority-30d", "🔵 Within 30 Days"),
            ]:
                items = prioritization.get(timeline, [])
                if items:
                    html += f'<h3>{label}</h3><div class="priority-section">'
                    for item in items:
                        html += f'<div class="priority-item {css_class}"><span class="severity-badge sev-{item.get("severity", "MEDIUM")}">{item.get("severity", "")}</span> {item.get("title", "")}</div>'
                    html += '</div>'

            html += "</div>"

        # Detailed Vulnerabilities
        if vulns:
            html += """
    <div class="section">
        <h2>🔍 Detailed Vulnerability Findings</h2>
"""
            for i, vuln in enumerate(vulns, 1):
                sev = vuln.get("severity", "MEDIUM")
                html += f"""
        <div class="vuln-card">
            <div class="vuln-title">
                <span class="severity-badge sev-{sev}">{sev}</span>
                #{i} — {vuln.get('title', 'Unknown')}
            </div>
            <div class="vuln-meta">
                {vuln.get('cwe_id', '')} | CVSS: {vuln.get('cvss_score', 0)} | 
                {vuln.get('owasp', '')} | Exploit Difficulty: {vuln.get('exploit_difficulty', 'N/A')}
            </div>
            <div class="explanation">{vuln.get('simple_explanation', '')}</div>
"""
                if vuln.get("real_world_example"):
                    html += f'<p style="font-size:13px;color:#aaa;margin:8px 0;"><strong>Real-world example:</strong> {vuln["real_world_example"]}</p>'

                fix = vuln.get("fix_instructions", {})
                if fix:
                    html += '<h3>Fix Instructions</h3>'
                    for platform, code in fix.items():
                        html += f'<p style="font-size:12px;color:#888;margin:4px 0 2px;">{platform.upper()}:</p>'
                        html += f'<div class="fix-code">{code}</div>'

                html += '</div>'

            html += '</div>'

        # Compliance Summary
        if compliance and compliance.get("frameworks"):
            html += """
    <div class="section">
        <h2>✅ Compliance Summary</h2>
        <div class="compliance-grid">
"""
            for fw_name, fw_data in compliance["frameworks"].items():
                status = fw_data.get("status", "UNKNOWN")
                css = "compliant" if status == "COMPLIANT" else "non-compliant"
                icon = "✅" if status == "COMPLIANT" else "❌"
                violations_count = len(fw_data.get("violations", []))
                html += f"""
            <div class="compliance-item {css}">
                <strong>{icon} {fw_name}</strong><br>
                <small>{fw_data.get('description', '')}</small><br>
                <small style="color:{'#00ff9d' if css == 'compliant' else '#ff003c'};">
                    {status}{f' ({violations_count} violations)' if violations_count else ''}
                </small>
            </div>
"""
            html += """
        </div>
    </div>
"""

        # Footer
        html += f"""
    <div class="footer">
        <p>🛡️ CyberGuardX Security Assessment Report</p>
        <p>Generated on {timestamp} | This report contains passive security analysis only</p>
        <p>DISCLAIMER: This is an educational tool. Findings should be verified by qualified security professionals.</p>
    </div>
</div>
</body>
</html>"""

        return html
