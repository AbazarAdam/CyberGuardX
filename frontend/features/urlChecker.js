/**
 * URL Phishing Checker Feature
 * Analyzes URLs for phishing indicators using ML model
 */

import { isValidURL } from '../js/validators.js';
import { getRiskBadge, formatFeatureName } from '../js/formatters.js';

const API_BASE_URL = 'http://localhost:8000';

export function initURLChecker(elements, uiHelpers) {
    const { checkUrlBtn, urlInput } = elements;

    checkUrlBtn.addEventListener('click', () => checkURL(elements, uiHelpers));
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') checkURL(elements, uiHelpers);
    });
}

function showError(container, message) {
    container.innerHTML = `<div class="error-message"><strong>Error:</strong> ${message}</div>`;
    container.classList.add('show');
}

function getStatusClass(isNegative) {
    return isNegative ? 'status-danger' : 'status-safe';
}

async function checkURL(elements, uiHelpers) {
    const { urlInput, urlResult, checkUrlBtn } = elements;
    const { showLoading, hideLoading } = uiHelpers;

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
