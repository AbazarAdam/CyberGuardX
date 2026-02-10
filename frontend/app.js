/**
 * CyberGuardX Frontend Application
 * Professional-grade security assessment platform
 * Features: Email breach detection, URL phishing, Password analysis, Website security scanning
 */

const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const emailInput = document.getElementById('emailInput');
const urlInput = document.getElementById('urlInput');
const websiteInput = document.getElementById('websiteInput');
const passwordInput = document.getElementById('passwordInput');
const checkEmailBtn = document.getElementById('checkEmailBtn');
const checkUrlBtn = document.getElementById('checkUrlBtn');
const scanWebsiteBtn = document.getElementById('scanWebsiteBtn');
const checkPasswordBtn = document.getElementById('checkPasswordBtn');
const generatePasswordBtn = document.getElementById('generatePasswordBtn');
const generatePassphraseBtn = document.getElementById('generatePassphraseBtn');
const showPasswordCheckbox = document.getElementById('showPassword');
const loadHistoryBtn = document.getElementById('loadHistoryBtn');
const emailResult = document.getElementById('emailResult');
const urlResult = document.getElementById('urlResult');
const websiteResult = document.getElementById('websiteResult');
const passwordResult = document.getElementById('passwordResult');
const historyResult = document.getElementById('historyResult');
const loadingOverlay = document.getElementById('loadingOverlay');
const confirmPermission = document.getElementById('confirmPermission');
const confirmOwner = document.getElementById('confirmOwner');
const confirmLegal = document.getElementById('confirmLegal');

// Toggle password visibility
if (showPasswordCheckbox) {
    showPasswordCheckbox.addEventListener('change', () => {
        passwordInput.type = showPasswordCheckbox.checked ? 'text' : 'password';
    });
}

function showLoading() { loadingOverlay.classList.add('show'); }
function hideLoading() { loadingOverlay.classList.remove('show'); }

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidURL(url) {
    try { new URL(url); return url.startsWith('http://') || url.startsWith('https://'); }
    catch { return false; }
}

function getRiskBadge(riskLevel) {
    const riskClass = `risk-${riskLevel.toLowerCase()}`;
    return `<span class="risk-badge ${riskClass}">${riskLevel}</span>`;
}

function getStatusClass(isNegative) {
    return isNegative ? 'status-danger' : 'status-safe';
}

function showError(container, message) {
    container.innerHTML = `<div class="error-message"><strong>Error:</strong> ${message}</div>`;
    container.classList.add('show');
}

function getSeverityBadge(severity) {
    const colors = { CRITICAL: '#ff003c', HIGH: '#ff6600', MEDIUM: '#ffaa00', LOW: '#00ff9d' };
    const color = colors[severity] || '#888';
    return `<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:bold;color:#000;background:${color};">${severity}</span>`;
}

function getGradeClass(grade) {
    if (!grade) return 'grade-f';
    if (grade.startsWith('A')) return 'grade-a';
    if (grade.startsWith('B')) return 'grade-b';
    if (grade.startsWith('C')) return 'grade-c';
    if (grade.startsWith('D')) return 'grade-d';
    return 'grade-f';
}

function getGradeColor(grade) {
    const colors = { A: '#00ff9d', B: '#00f3ff', C: '#ffaa00', D: '#ff6600', F: '#ff003c' };
    return colors[grade?.[0]] || '#888';
}

function getStrengthColor(strength) {
    const colors = { 'EXCELLENT': '#00ff9d', 'STRONG': '#00f3ff', 'MODERATE': '#ffaa00', 'WEAK': '#ff6600', 'VERY WEAK': '#ff003c' };
    return colors[strength] || '#888';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFeatureName(name) {
    return name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

// ============================================================
// PASSWORD STRENGTH ANALYZER
// ============================================================

async function checkPassword() {
    const password = passwordInput.value;
    if (!password) { showError(passwordResult, 'Please enter a password.'); return; }

    checkPasswordBtn.disabled = true;
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/check-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password }),
        });
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();
        displayPasswordResult(data);
    } catch (error) {
        showError(passwordResult, `Failed to analyze password. ${error.message}`);
    } finally {
        hideLoading();
        checkPasswordBtn.disabled = false;
    }
}

async function generatePassword(mode) {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/generate-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ length: 20, mode: mode }),
        });
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();
        passwordInput.value = data.password;
        passwordInput.type = 'text';
        if (showPasswordCheckbox) showPasswordCheckbox.checked = true;
        checkPassword();
    } catch (error) {
        showError(passwordResult, `Failed to generate password. ${error.message}`);
        hideLoading();
    }
}

function displayPasswordResult(data) {
    const strengthColor = getStrengthColor(data.strength);
    const scoreWidth = data.score;
    const charAnalysis = data.character_analysis || {};

    let patternsHTML = '';
    if (data.patterns_detected && data.patterns_detected.length > 0) {
        patternsHTML = `
            <div class="password-patterns">
                <h4>&#9888;&#65039; Patterns Detected</h4>
                <ul>${data.patterns_detected.map(p => `<li>${p}</li>`).join('')}</ul>
            </div>`;
    }

    let crackTimesHTML = '';
    if (data.crack_time_estimates) {
        const ct = data.crack_time_estimates;
        crackTimesHTML = `
            <div class="crack-times">
                <h4>&#9201;&#65039; Time to Crack</h4>
                <div class="crack-grid">
                    <div class="crack-item"><span class="crack-label">Online Attack:</span><span class="crack-value">${ct.online_attack || 'N/A'}</span></div>
                    <div class="crack-item"><span class="crack-label">Offline (bcrypt):</span><span class="crack-value">${ct.offline_slow_hash || 'N/A'}</span></div>
                    <div class="crack-item"><span class="crack-label">Offline (MD5):</span><span class="crack-value">${ct.offline_fast_hash || 'N/A'}</span></div>
                    <div class="crack-item"><span class="crack-label">GPU Cluster:</span><span class="crack-value">${ct.gpu_cluster || 'N/A'}</span></div>
                </div>
            </div>`;
    }

    let breachHTML = '';
    if (data.breach_check) {
        const bc = data.breach_check;
        breachHTML = `
            <div class="breach-check-result ${bc.found_in_breach_db ? 'breached' : 'safe'}">
                <strong>${bc.found_in_breach_db ? '&#9888;&#65039; Found in breach database!' : '&#9989; Not found in breach database'}</strong>
                <p>${bc.recommendation}</p>
            </div>`;
    }

    let issuesHTML = '';
    if (data.issues && data.issues.length > 0) {
        issuesHTML = `
            <div class="password-issues">
                <h4>&#128269; Issues Found (${data.issues.length})</h4>
                <ul>${data.issues.map(i => `<li>${i}</li>`).join('')}</ul>
            </div>`;
    }

    let recsHTML = '';
    if (data.recommendations && data.recommendations.length > 0) {
        recsHTML = `
            <div class="password-recommendations">
                <h4>&#128161; Recommendations</h4>
                <ul>${data.recommendations.map(r => `<li>${r}</li>`).join('')}</ul>
            </div>`;
    }

    passwordResult.innerHTML = `
        <div class="password-analysis">
            <div class="password-score-header">
                <div class="strength-label" style="color:${strengthColor};">${data.strength}</div>
                <div class="score-display">${data.score}/100</div>
            </div>
            <div class="score-bar-container">
                <div class="score-bar" style="width:${scoreWidth}%;background:${strengthColor};"></div>
            </div>
            <div class="password-metrics">
                <div class="metric-item"><span class="metric-label">Length:</span> <span class="metric-value">${data.password_length}</span></div>
                <div class="metric-item"><span class="metric-label">Entropy:</span> <span class="metric-value">${data.entropy_bits} bits</span></div>
                <div class="metric-item"><span class="metric-label">Charset Size:</span> <span class="metric-value">${data.charset_size}</span></div>
            </div>
            <div class="char-analysis">
                <span class="char-badge ${charAnalysis.has_uppercase ? 'present' : 'missing'}">A-Z ${charAnalysis.has_uppercase ? '&#10003;' : '&#10007;'}</span>
                <span class="char-badge ${charAnalysis.has_lowercase ? 'present' : 'missing'}">a-z ${charAnalysis.has_lowercase ? '&#10003;' : '&#10007;'}</span>
                <span class="char-badge ${charAnalysis.has_digits ? 'present' : 'missing'}">0-9 ${charAnalysis.has_digits ? '&#10003;' : '&#10007;'}</span>
                <span class="char-badge ${charAnalysis.has_special ? 'present' : 'missing'}">!@# ${charAnalysis.has_special ? '&#10003;' : '&#10007;'}</span>
            </div>
            ${breachHTML}
            ${crackTimesHTML}
            ${patternsHTML}
            ${issuesHTML}
            ${recsHTML}
        </div>
    `;
    passwordResult.classList.add('show');
}

// ============================================================
// EMAIL BREACH CHECKER
// ============================================================

async function checkEmail() {
    const email = emailInput.value.trim();
    if (!email) { showError(emailResult, 'Please enter an email address.'); return; }
    if (!isValidEmail(email)) { showError(emailResult, 'Please enter a valid email address.'); return; }

    emailResult.classList.remove('show');
    checkEmailBtn.disabled = true;
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/check-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
        });
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();

        const statusClass = getStatusClass(data.breached);
        const statusText = data.breached ? '&#9888;&#65039; Breached' : '&#10003; Safe';

        let breachesHTML = '';
        if (data.breaches && data.breaches.length > 0) {
            breachesHTML = `
                <div class="breach-timeline">
                    <div class="breach-timeline-header">
                        <h4>&#128202; Breach Timeline</h4>
                        <span class="breach-count-badge">${data.pwned_count} breach${data.pwned_count > 1 ? 'es' : ''} found</span>
                    </div>
                    ${data.total_accounts_affected ? `
                        <div class="total-impact-banner">
                            <span class="impact-icon">&#9888;&#65039;</span>
                            <span class="impact-text">Total impact: <strong>${data.total_accounts_affected.toLocaleString()}</strong> accounts across all breaches</span>
                        </div>` : ''}
                    <div class="breach-list">
                        ${data.breaches.map((breach, index) => `
                            <div class="breach-item ${breach.severity ? breach.severity.toLowerCase() : 'medium'}">
                                <div class="breach-number">${index + 1}</div>
                                <div class="breach-content">
                                    <div class="breach-header">
                                        <div class="breach-title-row">
                                            <span class="breach-name">&#128274; ${breach.title || breach.name}</span>
                                            ${breach.severity ? `<span class="severity-badge ${breach.severity.toLowerCase()}">${breach.severity}</span>` : ''}
                                        </div>
                                        <span class="breach-date">&#128197; ${breach.date}</span>
                                    </div>
                                    <div class="breach-details">
                                        <div class="breach-stat"><span class="stat-label">&#128202; Accounts:</span> <span class="stat-value">${breach.accounts.toLocaleString()}</span></div>
                                        <div class="breach-data-classes">
                                            <strong>&#128274; Data exposed:</strong>
                                            <div class="data-class-tags">
                                                ${breach.data_classes.map(dc => {
                                                    const isSensitive = /password|credit|ssn|bank|financial/i.test(dc);
                                                    return `<span class="data-class-tag ${isSensitive ? 'sensitive' : ''}">${dc}</span>`;
                                                }).join('')}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>`;
        }

        let recommendationsHTML = '';
        if (data.recommendations && data.recommendations.length > 0) {
            recommendationsHTML = `
                <div class="recommendations-section">
                    <h4>&#128161; Security Recommendations</h4>
                    <ul class="recommendations-list">${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}</ul>
                </div>`;
        }

        emailResult.innerHTML = `
            <div class="result-header">
                <div class="result-status ${statusClass}">${statusText}</div>
                ${getRiskBadge(data.risk_level)}
            </div>
            <div class="result-details">
                <div class="result-item"><span class="result-label">Email:</span><span class="result-value">${data.email}</span></div>
                <div class="result-item"><span class="result-label">Status:</span><span class="result-value">${data.message}</span></div>
                ${data.pwned_count > 0 ? `<div class="result-item pwned-count-highlight"><span class="result-label">Times Pwned:</span><span class="result-value pwned-count-badge">${data.pwned_count}</span></div>` : ''}
                <div class="result-item"><span class="result-label">Risk Level:</span><span class="result-value">${data.risk_level}</span></div>
            </div>
            ${breachesHTML}
            ${recommendationsHTML}
        `;
        emailResult.classList.add('show');
    } catch (error) {
        showError(emailResult, `Failed to check email. ${error.message}`);
    } finally {
        hideLoading();
        checkEmailBtn.disabled = false;
    }
}

// ============================================================
// URL PHISHING CHECKER
// ============================================================

async function checkURL() {
    const url = urlInput.value.trim();
    if (!url) { showError(urlResult, 'Please enter a URL.'); return; }
    if (!isValidURL(url)) { showError(urlResult, 'Please enter a valid URL (must start with http:// or https://).'); return; }

    urlResult.classList.remove('show');
    checkUrlBtn.disabled = true;
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/check-url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url }),
        });
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();

        const confidence = data.confidence ? (data.confidence * 100).toFixed(1) : (data.phishing_score * 100).toFixed(1);
        const statusClass = getStatusClass(data.is_phishing);
        const statusText = data.is_phishing ? '&#9888;&#65039; Phishing Detected' : '&#10003; Legitimate';

        let mlExplainabilityHTML = '';
        if (data.feature_analysis && data.feature_analysis.length > 0) {
            mlExplainabilityHTML = `
                <div class="ml-explainability-section">
                    <h4>&#129302; AI Analysis</h4>
                    ${data.model_info ? `
                        <div class="model-info">
                            <div class="model-info-item"><span class="label">Model:</span> <span class="value">${data.model_info.name} v${data.model_info.version}</span></div>
                            <div class="model-info-item"><span class="label">Confidence:</span> <span class="value">${confidence}%</span></div>
                        </div>` : ''}
                    <div class="feature-analysis">
                        <h5>&#128269; Risk Factors</h5>
                        ${data.feature_analysis.map(f => `
                            <div class="feature-item">
                                <div class="feature-header">
                                    <span class="feature-name">${formatFeatureName(f.feature)}</span>
                                    <span class="feature-impact">${(f.impact * 100).toFixed(1)}% impact</span>
                                    <span class="risk-badge risk-${f.risk.toLowerCase()}">${f.risk}</span>
                                </div>
                                <div class="feature-explanation">${f.explanation}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>`;
        }

        urlResult.innerHTML = `
            <div class="result-header">
                <div class="result-status ${statusClass}">${statusText}</div>
                ${getRiskBadge(data.risk_level)}
            </div>
            <div class="result-details">
                <div class="result-item"><span class="result-label">URL:</span><span class="result-value" style="word-break:break-all;">${data.url}</span></div>
                <div class="result-item"><span class="result-label">Phishing Score:</span><span class="result-value">${(data.phishing_score * 100).toFixed(1)}%</span></div>
                <div class="result-item"><span class="result-label">Confidence:</span><span class="result-value">${confidence}%</span></div>
            </div>
            ${mlExplainabilityHTML}
        `;
        urlResult.classList.add('show');
    } catch (error) {
        showError(urlResult, `Failed to check URL. ${error.message}`);
    } finally {
        hideLoading();
        checkUrlBtn.disabled = false;
    }
}

// ============================================================
// WEBSITE SECURITY SCANNER (Enhanced with deep vulnerability display)
// ============================================================

async function scanWebsite() {
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

        displayWebsiteResults(data);

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

function displayWebsiteResults(data) {
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

// ============================================================
// SCAN HISTORY
// ============================================================

async function loadHistory() {
    loadHistoryBtn.disabled = true;
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/scan-history`);
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();

        if (!data || data.length === 0) {
            historyResult.innerHTML = '<div style="text-align:center;padding:20px;color:#6b7280;">No scan history available.</div>';
        } else {
            let tableHTML = `
                <table class="history-table">
                    <thead><tr><th>Type</th><th>Target</th><th>Risk Level</th><th>Score</th><th>Timestamp</th></tr></thead>
                    <tbody>`;

            data.slice(0, 10).forEach(scan => {
                const type = scan.email === 'URL_SCAN' ? 'URL' : 'Email';
                const target = scan.email === 'URL_SCAN' ? 'URL Scan' : scan.email;
                const score = scan.phishing_score ? `${(scan.phishing_score * 100).toFixed(1)}%` : 'N/A';
                tableHTML += `
                    <tr>
                        <td><strong>${type}</strong></td>
                        <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;">${target}</td>
                        <td>${getRiskBadge(scan.risk_level)}</td>
                        <td>${score}</td>
                        <td style="font-size:0.85rem;">${new Date(scan.scanned_at).toLocaleString()}</td>
                    </tr>`;
            });
            tableHTML += '</tbody></table>';
            historyResult.innerHTML = tableHTML;
        }
        historyResult.classList.add('show');
    } catch (error) {
        historyResult.innerHTML = `<div class="error-message"><strong>Error:</strong> Failed to load history. ${error.message}</div>`;
        historyResult.classList.add('show');
    } finally {
        hideLoading();
        loadHistoryBtn.disabled = false;
    }
}

// ============================================================
// EVENT LISTENERS
// ============================================================

checkEmailBtn.addEventListener('click', checkEmail);
checkUrlBtn.addEventListener('click', checkURL);
scanWebsiteBtn.addEventListener('click', scanWebsite);
checkPasswordBtn.addEventListener('click', checkPassword);
generatePasswordBtn.addEventListener('click', () => generatePassword('random'));
generatePassphraseBtn.addEventListener('click', () => generatePassword('memorable'));
loadHistoryBtn.addEventListener('click', loadHistory);

emailInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') checkEmail(); });
urlInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') checkURL(); });
websiteInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') scanWebsite(); });
passwordInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') checkPassword(); });

console.log('CyberGuardX Frontend Loaded (Enhanced v2.0)');
console.log('Backend API:', API_BASE_URL);
