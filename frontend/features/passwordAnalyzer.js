/**
 * Password Strength Analyzer Feature
 * Analyzes password strength and generates secure passwords
 */

import { getStrengthColor } from '../js/formatters.js';

const API_BASE_URL = 'http://localhost:8000';

export function initPasswordAnalyzer(elements, uiHelpers) {
    const { checkPasswordBtn, generatePasswordBtn, generatePassphraseBtn, passwordInput, showPasswordCheckbox } = elements;

    checkPasswordBtn.addEventListener('click', () => checkPassword(elements, uiHelpers));
    generatePasswordBtn.addEventListener('click', () => generatePassword('random', elements, uiHelpers));
    generatePassphraseBtn.addEventListener('click', () => generatePassword('memorable', elements, uiHelpers));
    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') checkPassword(elements, uiHelpers);
    });

    // Toggle password visibility
    if (showPasswordCheckbox) {
        showPasswordCheckbox.addEventListener('change', () => {
            passwordInput.type = showPasswordCheckbox.checked ? 'text' : 'password';
        });
    }
}

function showError(container, message) {
    container.innerHTML = `<div class="error-message"><strong>Error:</strong> ${message}</div>`;
    container.classList.add('show');
}

async function checkPassword(elements, uiHelpers) {
    const { passwordInput, passwordResult, checkPasswordBtn } = elements;
    const { showLoading, hideLoading } = uiHelpers;

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
        displayPasswordResult(data, passwordResult);
    } catch (error) {
        showError(passwordResult, `Failed to analyze password. ${error.message}`);
    } finally {
        hideLoading();
        checkPasswordBtn.disabled = false;
    }
}

async function generatePassword(mode, elements, uiHelpers) {
    const { passwordInput, passwordResult, showPasswordCheckbox } = elements;
    const { showLoading, hideLoading } = uiHelpers;

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
        checkPassword(elements, uiHelpers);
    } catch (error) {
        showError(passwordResult, `Failed to generate password. ${error.message}`);
        hideLoading();
    }
}

function displayPasswordResult(data, passwordResult) {
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
