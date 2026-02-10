/**
 * Email Breach Checker Feature
 * Checks if email has been compromised in data breaches
 */

import { isValidEmail } from '../js/validators.js';
import { getRiskBadge } from '../js/formatters.js';

const API_BASE_URL = 'http://localhost:8000';

export function initEmailChecker(elements, uiHelpers) {
    const { checkEmailBtn, emailInput } = elements;

    checkEmailBtn.addEventListener('click', () => checkEmail(elements, uiHelpers));
    emailInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') checkEmail(elements, uiHelpers);
    });
}

function showError(container, message) {
    container.innerHTML = `<div class="error-message"><strong>Error:</strong> ${message}</div>`;
    container.classList.add('show');
}

function getStatusClass(isNegative) {
    return isNegative ? 'status-danger' : 'status-safe';
}

async function checkEmail(elements, uiHelpers) {
    const { emailInput, emailResult, checkEmailBtn } = elements;
    const { showLoading, hideLoading } = uiHelpers;

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
