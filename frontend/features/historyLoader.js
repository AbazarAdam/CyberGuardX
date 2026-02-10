/**
 * History Loader Feature
 * Loads and displays scan history with pagination
 */

import { getRiskBadge } from '../js/formatters.js';

const API_BASE_URL = 'http://localhost:8000';
const PAGE_SIZE = 20;

let currentPage = 0;

export function initHistoryLoader(elements, uiHelpers) {
    const { loadHistoryBtn } = elements;
    loadHistoryBtn.addEventListener('click', () => {
        currentPage = 0;
        loadHistory(elements, uiHelpers);
    });
}

async function loadHistory(elements, uiHelpers) {
    const { loadHistoryBtn, historyResult } = elements;
    const { showLoading, hideLoading } = uiHelpers;

    loadHistoryBtn.disabled = true;
    showLoading();

    const skip = currentPage * PAGE_SIZE;

    try {
        const response = await fetch(
            `${API_BASE_URL}/scan-history?skip=${skip}&limit=${PAGE_SIZE}`
        );
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();

        if (!data || data.length === 0) {
            if (currentPage === 0) {
                historyResult.innerHTML =
                    '<div style="text-align:center;padding:20px;color:#6b7280;">No scan history available.</div>';
            } else {
                historyResult.innerHTML =
                    '<div style="text-align:center;padding:20px;color:#6b7280;">No more records.</div>';
            }
        } else {
            let tableHTML = `
                <table class="history-table">
                    <thead><tr><th>Type</th><th>Target</th><th>Risk Level</th><th>Score</th><th>Timestamp</th></tr></thead>
                    <tbody>`;

            data.forEach(scan => {
                const type = scan.email === 'URL_SCAN' || scan.email === 'URL Check' ? 'URL' : 'Email';
                const target = type === 'URL' ? 'URL Scan' : scan.email;
                const score = scan.phishing_score != null
                    ? `${(scan.phishing_score * 100).toFixed(1)}%`
                    : 'N/A';
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

            // Pagination controls
            const pageNum = currentPage + 1;
            const hasPrev = currentPage > 0;
            const hasNext = data.length === PAGE_SIZE;

            tableHTML += `
                <div class="pagination-controls" style="display:flex;justify-content:center;align-items:center;gap:12px;margin-top:16px;">
                    <button id="historyPrev" class="btn btn-sm" ${hasPrev ? '' : 'disabled'}
                        style="padding:6px 14px;font-size:0.85rem;">Previous</button>
                    <span style="color:#94a3b8;font-size:0.85rem;">Page ${pageNum}</span>
                    <button id="historyNext" class="btn btn-sm" ${hasNext ? '' : 'disabled'}
                        style="padding:6px 14px;font-size:0.85rem;">Next</button>
                </div>`;

            historyResult.innerHTML = tableHTML;

            // Attach pagination handlers
            const prevBtn = document.getElementById('historyPrev');
            const nextBtn = document.getElementById('historyNext');
            if (prevBtn) {
                prevBtn.addEventListener('click', () => {
                    currentPage--;
                    loadHistory(elements, uiHelpers);
                });
            }
            if (nextBtn) {
                nextBtn.addEventListener('click', () => {
                    currentPage++;
                    loadHistory(elements, uiHelpers);
                });
            }
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
