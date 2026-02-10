/**
 * Website Security Scanner Feature
 * Comprehensive security assessment with vulnerability detection
 */

import { isValidURL } from '../js/validators.js';
import { getRiskBadge, getSeverityBadge, getGradeClass, getGradeColor } from '../js/formatters.js';

const API_BASE_URL = 'http://localhost:8000';

export function initWebsiteScanner(elements, uiHelpers) {
    const { scanWebsiteBtn, websiteInput } = elements;

    scanWebsiteBtn.addEventListener('click', () => scanWebsite(elements, uiHelpers));
    websiteInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') scanWebsite(elements, uiHelpers);
    });
}

function showError(container, message) {
    container.innerHTML = `<div class="error-message"><strong>Error:</strong> ${message}</div>`;
    container.classList.add('show');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function scanWebsite(elements, uiHelpers) {
    const { websiteInput, websiteResult, scanWebsiteBtn, confirmPermission, confirmOwner, confirmLegal } = elements;

    const url = websiteInput.value.trim();
    if (!url) { showError(websiteResult, 'Please enter a website URL.'); return; }
    if (!isValidURL(url)) { showError(websiteResult, 'Please enter a valid URL (must start with http:// or https://).'); return; }
    if (!confirmPermission.checked || !confirmOwner.checked || !confirmLegal.checked) {
        showError(websiteResult, 'You must accept all legal disclaimers before scanning.');
        return;
    }

    websiteResult.classList.remove('show');
    scanWebsiteBtn.disabled = true;

    const progressContainer = document.getElementById('websiteScanProgress');
    progressContainer.style.display = 'block';
    progressContainer.innerHTML = '';
    let progressTracker = null;

    try {
        const response = await fetch(`${API_BASE_URL}/scan-website`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url,
                confirmed_permission: confirmPermission.checked,
                owner_confirmation: confirmOwner.checked,
                legal_responsibility: confirmLegal.checked
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }

        const data = await response.json();

        if (data.progress_scan_id && typeof ScanProgressTracker !== 'undefined') {
            progressTracker = new ScanProgressTracker('websiteScanProgress');
            progressTracker.startTracking(data.progress_scan_id, url);
        }

        displayWebsiteResults(data, websiteResult);

        if (progressContainer && progressTracker) {
            setTimeout(() => { progressContainer.classList.add('minimized'); }, 3000);
        }
    } catch (error) {
        showError(websiteResult, `Failed to scan website. ${error.message}`);
        if (progressContainer) progressContainer.classList.add('minimized');
    } finally {
        scanWebsiteBtn.disabled = false;
    }
}

function displayWebsiteResults(data, websiteResult) {
    const vulnAnalysis = data.vulnerability_analysis || {};
    const vulns = vulnAnalysis.vulnerabilities || [];
    const severityCounts = vulnAnalysis.severity_counts || {};
    const scorecard = vulnAnalysis.security_scorecard || {};
    const compliance = vulnAnalysis.compliance_summary || {};
    const prioritization = vulnAnalysis.risk_prioritization || {};
    const waf = vulnAnalysis.waf_detection || {};

    // Build vulnerability cards
    let vulnCardsHTML = '';
    if (vulns.length > 0) {
        vulnCardsHTML = `
            <div class="vuln-findings">
                <h4>&#128269; Vulnerability Findings (${vulns.length})</h4>
                ${vulns.map((v, i) => `
                    <div class="vuln-card" onclick="this.classList.toggle('expanded')">
                        <div class="vuln-card-header">
                            ${getSeverityBadge(v.severity)}
                            <span class="vuln-title">${v.title}</span>
                            <span class="vuln-cvss">CVSS ${v.cvss_score}</span>
                            <span class="vuln-expand-icon">&#9660;</span>
                        </div>
                        <div class="vuln-card-body">
                            <div class="vuln-meta-row">
                                <span>${v.cwe_id}</span> | <span>${v.owasp}</span> | 
                                <span>Exploit: ${v.exploit_difficulty}</span> | 
                                <span>Fix within: ${v.priority_timeframe}</span>
                            </div>
                            <div class="vuln-explanation">
                                <strong>What this means:</strong> ${v.simple_explanation}
                            </div>
                            ${v.real_world_example ? `
                                <div class="vuln-example">
                                    <strong>Real-world example:</strong> ${v.real_world_example}
                                </div>` : ''}
                            ${v.fix_instructions ? `
                                <div class="vuln-fix">
                                    <strong>How to fix:</strong>
                                    <div class="fix-tabs">
                                        ${Object.entries(v.fix_instructions).map(([platform, code]) => `
                                            <div class="fix-tab">
                                                <div class="fix-tab-label">${platform.toUpperCase()}</div>
                                                <pre class="fix-code">${escapeHtml(code)}</pre>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>` : ''}
                            ${v.compliance && v.compliance.length > 0 ? `
                                <div class="vuln-compliance">
                                    <strong>Compliance:</strong> ${v.compliance.join(', ')}
                                </div>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>`;
    }

    // Security scorecard
    let scorecardHTML = '';
    if (scorecard.categories) {
        scorecardHTML = `
            <div class="security-scorecard">
                <h4>&#128203; Security Scorecard</h4>
                <div class="scorecard-grid">
                    ${Object.entries(scorecard.categories).map(([name, cat]) => `
                        <div class="scorecard-item">
                            <div class="sc-grade" style="color:${getGradeColor(cat.grade)}">${cat.grade}</div>
                            <div class="sc-score">${cat.score}/100</div>
                            <div class="sc-label">${name}</div>
                        </div>
                    `).join('')}
                </div>
            </div>`;
    }

    // Compliance summary
    let complianceHTML = '';
    if (compliance.frameworks) {
        complianceHTML = `
            <div class="compliance-section">
                <h4>&#9989; Compliance Status (${compliance.compliance_percentage || 0}%)</h4>
                <div class="compliance-grid">
                    ${Object.entries(compliance.frameworks).map(([name, fw]) => `
                        <div class="compliance-item ${fw.status === 'COMPLIANT' ? 'compliant' : 'non-compliant'}">
                            <span class="compliance-icon">${fw.status === 'COMPLIANT' ? '&#9989;' : '&#10060;'}</span>
                            <span class="compliance-name">${name}</span>
                            ${fw.violations && fw.violations.length > 0 ? `<span class="compliance-violations">${fw.violations.length} violations</span>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>`;
    }

    // WAF detection
    let wafHTML = '';
    if (waf) {
        wafHTML = `
            <div class="waf-status ${waf.waf_detected ? 'protected' : 'unprotected'}">
                <span class="waf-icon">${waf.waf_detected ? '&#128737;&#65039;' : '&#9888;&#65039;'}</span>
                <span>WAF: ${waf.waf_detected ? `Protected (${waf.detected_wafs.join(', ')})` : 'No WAF Detected'}</span>
            </div>`;
    }

    // Priority timeline
    let priorityHTML = '';
    if (prioritization) {
        const sections = [
            { key: 'immediate', label: '&#128308; IMMEDIATE', css: 'priority-immediate' },
            { key: 'within_24_hours', label: '&#128992; 24 Hours', css: 'priority-24h' },
            { key: 'within_7_days', label: '&#128993; 7 Days', css: 'priority-7d' },
            { key: 'within_30_days', label: '&#128309; 30 Days', css: 'priority-30d' },
        ];
        const hasItems = sections.some(s => (prioritization[s.key] || []).length > 0);
        if (hasItems) {
            priorityHTML = `<div class="priority-timeline"><h4>&#9201;&#65039; Remediation Priority</h4>`;
            for (const s of sections) {
                const items = prioritization[s.key] || [];
                if (items.length > 0) {
                    priorityHTML += `<div class="priority-group"><div class="priority-label ${s.css}">${s.label}</div>`;
                    items.forEach(item => {
                        priorityHTML += `<div class="priority-item ${s.css}">${getSeverityBadge(item.severity)} ${item.title}</div>`;
                    });
                    priorityHTML += `</div>`;
                }
            }
            priorityHTML += `</div>`;
        }
    }

    // Build main results
    websiteResult.innerHTML = `
        <div class="scan-summary">
            <div class="scan-header">
                <h3>&#128737;&#65039; Security Assessment Complete</h3>
                <span class="scan-duration">${data.scan_duration_ms}ms</span>
            </div>
            
            <div class="overall-grade">
                <div class="grade-display ${getGradeClass(data.overall_grade)}">
                    ${data.overall_grade}
                </div>
                <div class="grade-details">
                    <div class="grade-item">Risk Score: <strong>${data.risk_score}/100</strong></div>
                    <div class="grade-item">Risk Level: ${getRiskBadge(data.risk_level)}</div>
                    <div class="grade-item">Security: <strong>${data.security_posture}</strong></div>
                </div>
            </div>
            
            ${wafHTML}
            
            <div class="component-grades">
                <div class="component-grade">
                    <div class="component-label">HTTP Headers</div>
                    <div class="grade-badge ${getGradeClass(data.http_grade)}">${data.http_grade}</div>
                </div>
                <div class="component-grade">
                    <div class="component-label">SSL/TLS</div>
                    <div class="grade-badge ${getGradeClass(data.ssl_grade)}">${data.ssl_grade}</div>
                </div>
                <div class="component-grade">
                    <div class="component-label">DNS Security</div>
                    <div class="grade-badge ${getGradeClass(data.dns_grade)}">${data.dns_grade}</div>
                </div>
                <div class="component-grade">
                    <div class="component-label">Technology</div>
                    <div class="grade-badge ${getGradeClass(data.tech_grade)}">${data.tech_grade}</div>
                </div>
            </div>
            
            <div class="issues-summary">
                <div class="issue-count critical">
                    <span class="count">${severityCounts.critical || 0}</span>
                    <span class="label">Critical</span>
                </div>
                <div class="issue-count high">
                    <span class="count">${severityCounts.high || 0}</span>
                    <span class="label">High</span>
                </div>
                <div class="issue-count medium">
                    <span class="count">${severityCounts.medium || 0}</span>
                    <span class="label">Medium</span>
                </div>
                <div class="issue-count low">
                    <span class="count">${severityCounts.low || 0}</span>
                    <span class="label">Low</span>
                </div>
            </div>
            
            ${scorecardHTML}
            ${priorityHTML}
            ${vulnCardsHTML}
            ${complianceHTML}
            
            <div class="owasp-compliance">
                <h4>&#128202; OWASP Top 10 Compliance</h4>
                <div class="compliance-score">
                    Score: <strong>${data.owasp_compliance_score}/100</strong> | 
                    Compliant: ${data.compliant_categories} | 
                    Non-Compliant: ${data.non_compliant_categories}
                </div>
            </div>
            
            ${data.recommendations && data.recommendations.length > 0 ? `
                <div class="recommendations"><h4>&#128295; Recommendations</h4><ul>
                    ${data.recommendations.slice(0, 8).map(r => `<li>${r}</li>`).join('')}
                </ul></div>` : ''}
            
            <div class="report-actions">
                <button class="btn btn-primary" onclick="window.open('${API_BASE_URL}/generate-report/${data.scan_id}', '_blank')">
                    &#128196; View Full Report
                </button>
            </div>
            
            <div class="scan-footer">
                <small>Scan ID: ${data.scan_id} | ${new Date(data.scan_timestamp).toLocaleString()}</small>
            </div>
        </div>
    `;
    websiteResult.classList.add('show');
}
