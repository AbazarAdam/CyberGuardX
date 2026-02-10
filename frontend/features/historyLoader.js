/**
 * History Loader Feature
 * Loads and displays scan history from the backend
 */

import { getRiskBadge } from '../js/formatters.js';

const API_BASE_URL = 'http://localhost:8000';

export function initHistoryLoader(elements, uiHelpers) {
    const { loadHistoryBtn, historyResult } = elements;
    const { showLoading, hideLoading } = uiHelpers;

    loadHistoryBtn.addEventListener('click', () => loadHistory(elements, uiHelpers));
}

async function loadHistory(elements, uiHelpers) {
    const { loadHistoryBtn, historyResult } = elements;
    const { showLoading, hideLoading } = uiHelpers;

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
