/**
 * Formatters Module
 * UI formatting utilities for badges, labels, and display elements
 */

export const formatters = {
    /**
     * Get risk level badge HTML
     */
    getRiskBadge(riskLevel) {
        const riskClass = `risk-${riskLevel.toLowerCase()}`;
        return `<span class="risk-badge ${riskClass}">${riskLevel}</span>`;
    },

    /**
     * Get severity badge HTML
     */
    getSeverityBadge(severity) {
        const colors = {
            CRITICAL: '#ff003c',
            HIGH: '#ff6600',
            MEDIUM: '#ffaa00',
            LOW: '#00ff9d'
        };
        const color = colors[severity] || '#888';
        return `<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:bold;color:#000;background:${color};">${severity}</span>`;
    },

    /**
     * Get CSS class for grade
     */
    getGradeClass(grade) {
        if (!grade) return 'grade-f';
        if (grade.startsWith('A')) return 'grade-a';
        if (grade.startsWith('B')) return 'grade-b';
        if (grade.startsWith('C')) return 'grade-c';
        if (grade.startsWith('D')) return 'grade-d';
        return 'grade-f';
    },

    /**
     * Get color for grade
     */
    getGradeColor(grade) {
        const colors = {
            A: '#00ff9d',
            B: '#00f3ff',
            C: '#ffaa00',
            D: '#ff6600',
            F: '#ff003c'
        };
        return colors[grade?.[0]] || '#888';
    },

    /**
     * Get color for password strength
     */
    getStrengthColor(strength) {
        const colors = {
            'EXCELLENT': '#00ff9d',
            'STRONG': '#00f3ff',
            'MODERATE': '#ffaa00',
            'WEAK': '#ff6600',
            'VERY WEAK': '#ff003c'
        };
        return colors[strength] || '#888';
    },

    /**
     * Get CSS class for status
     */
    getStatusClass(isNegative) {
        return isNegative ? 'status-danger' : 'status-safe';
    },

    /**
     * Format feature name (snake_case to Title Case)
     */
    formatFeatureName(name) {
        return name.split('_')
            .map(w => w.charAt(0).toUpperCase() + w.slice(1))
            .join(' ');
    }
};
