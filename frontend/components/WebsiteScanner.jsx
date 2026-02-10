/**
 * CyberGuardX - Website Security Scanner Frontend Component
 * React component for performing ethical website security assessments
 */

import React, { useState } from 'react';
import './WebsiteScanner.css';

const WebsiteScanner = () => {
  const [url, setUrl] = useState('');
  const [legalAccepted, setLegalAccepted] = useState(false);
  const [ownerConfirmed, setOwnerConfirmed] = useState(false);
  const [responsibilityAccepted, setResponsibilityAccepted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState(null);
  const [rateLimitMessage, setRateLimitMessage] = useState(null);

  /**
   * Validates URL format
   */
  const isValidUrl = (urlString) => {
    try {
      const urlObj = new URL(urlString);
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  };

  /**
   * Handles scan button click
   */
  const handleScan = async () => {
    // Reset previous results
    setError(null);
    setScanResult(null);
    setRateLimitMessage(null);

    // Validation checks
    if (!url.trim()) {
      setError('Please enter a website URL');
      return;
    }

    if (!isValidUrl(url)) {
      setError('Please enter a valid URL (must start with http:// or https://)');
      return;
    }

    if (!legalAccepted || !ownerConfirmed || !responsibilityAccepted) {
      setError('You must accept all legal disclaimers to proceed');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/scan-website', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url.trim(),
          confirmed_permission: ownerConfirmed,
          owner_confirmation: ownerConfirmed,
          legal_responsibility: responsibilityAccepted,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 429) {
          setRateLimitMessage(data.detail || 'Rate limit exceeded. Please wait before scanning again.');
        } else if (response.status === 403) {
          setError(data.detail || 'Permission not confirmed');
        } else {
          setError(data.detail || 'Scan failed');
        }
        return;
      }

      setScanResult(data);
    } catch (err) {
      setError(`Network error: ${err.message}. Make sure the backend server is running.`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Gets color class based on risk level
   */
  const getRiskColor = (riskLevel) => {
    const colors = {
      'CRITICAL': 'risk-critical',
      'HIGH': 'risk-high',
      'MEDIUM': 'risk-medium',
      'LOW': 'risk-low',
      'MINIMAL': 'risk-minimal',
    };
    return colors[riskLevel] || 'risk-unknown';
  };

  /**
   * Gets color class based on grade
   */
  const getGradeColor = (grade) => {
    if (grade === 'A+' || grade === 'A') return 'grade-a';
    if (grade === 'B') return 'grade-b';
    if (grade === 'C') return 'grade-c';
    if (grade === 'D') return 'grade-d';
    return 'grade-f';
  };

  /**
   * Exports scan results as JSON
   */
  const exportJSON = () => {
    if (!scanResult) return;
    
    const dataStr = JSON.stringify(scanResult, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `cyberguardx-scan-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  /**
   * Checks if scan button should be enabled
   */
  const isScanEnabled = () => {
    return legalAccepted && ownerConfirmed && responsibilityAccepted && url.trim() && !loading;
  };

  return (
    <div className="website-scanner-container">
      <div className="scanner-header">
        <h1>🛡️ Website Security Scanner</h1>
        <p className="subtitle">Comprehensive Passive Security Assessment</p>
      </div>

      {/* Legal Disclaimer Section */}
      <div className="legal-disclaimer-box">
        <h3>⚖️ Legal Disclaimer & Terms of Use</h3>
        <p className="disclaimer-text">
          This tool performs PASSIVE security assessments only. You must have legal authorization
          to scan any website. Unauthorized scanning may violate computer fraud laws.
        </p>
        
        <div className="checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={ownerConfirmed}
              onChange={(e) => setOwnerConfirmed(e.target.checked)}
            />
            <span>☐ I confirm I own this website or have written permission to scan it</span>
          </label>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={legalAccepted}
              onChange={(e) => setLegalAccepted(e.target.checked)}
            />
            <span>☐ I understand scanning without permission may be illegal</span>
          </label>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={responsibilityAccepted}
              onChange={(e) => setResponsibilityAccepted(e.target.checked)}
            />
            <span>☐ I accept full legal responsibility for this scan</span>
          </label>
        </div>

        <div className="rate-limit-notice">
          <strong>Rate Limiting:</strong> Maximum 1 scan per 10 minutes per IP address
        </div>
      </div>

      {/* URL Input Section */}
      <div className="scan-input-section">
        <div className="input-group">
          <label htmlFor="url-input">Target Website URL</label>
          <input
            id="url-input"
            type="text"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
            className="url-input"
          />
        </div>

        <button
          onClick={handleScan}
          disabled={!isScanEnabled()}
          className={`scan-button ${isScanEnabled() ? 'enabled' : 'disabled'}`}
        >
          {loading ? '🔍 Scanning...' : '🚀 Start Security Scan'}
        </button>
      </div>

      {/* Error Messages */}
      {error && (
        <div className="alert alert-error">
          <strong>❌ Error:</strong> {error}
        </div>
      )}

      {rateLimitMessage && (
        <div className="alert alert-warning">
          <strong>⏳ Rate Limit:</strong> {rateLimitMessage}
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Running security assessment... This may take 10-30 seconds.</p>
        </div>
      )}

      {/* Scan Results */}
      {scanResult && (
        <div className="scan-results">
          {/* Executive Summary */}
          <div className="results-header">
            <h2>📊 Security Assessment Results</h2>
            <button onClick={exportJSON} className="export-button">
              📥 Export JSON
            </button>
          </div>

          <div className="summary-cards">
            <div className={`summary-card ${getGradeColor(scanResult.overall_grade)}`}>
              <h3>Overall Grade</h3>
              <div className="grade-display">{scanResult.overall_grade}</div>
              <p>{scanResult.security_posture}</p>
            </div>

            <div className={`summary-card ${getRiskColor(scanResult.risk_level)}`}>
              <h3>Risk Score</h3>
              <div className="risk-score-display">{scanResult.risk_score}/100</div>
              <p>{scanResult.risk_level} RISK</p>
            </div>

            <div className="summary-card">
              <h3>Issues Found</h3>
              <div className="issues-display">
                <span className="critical-count">{scanResult.critical_issues_count} Critical</span>
                <span className="high-count">{scanResult.high_issues_count} High</span>
              </div>
              <p>Scan time: {scanResult.scan_duration_ms}ms</p>
            </div>
          </div>

          {/* Component Grades */}
          <div className="component-grades">
            <h3>Component Security Grades</h3>
            <div className="grades-grid">
              <div className={`grade-item ${getGradeColor(scanResult.http_grade)}`}>
                <span className="grade-label">HTTP Headers</span>
                <span className="grade-value">{scanResult.http_grade}</span>
              </div>
              <div className={`grade-item ${getGradeColor(scanResult.ssl_grade)}`}>
                <span className="grade-label">SSL/TLS</span>
                <span className="grade-value">{scanResult.ssl_grade}</span>
              </div>
              <div className={`grade-item ${getGradeColor(scanResult.dns_grade)}`}>
                <span className="grade-label">DNS Security</span>
                <span className="grade-value">{scanResult.dns_grade}</span>
              </div>
              <div className={`grade-item ${getGradeColor(scanResult.tech_grade)}`}>
                <span className="grade-label">Technology</span>
                <span className="grade-value">{scanResult.tech_grade}</span>
              </div>
            </div>
          </div>

          {/* Top Risks */}
          {scanResult.top_risks && scanResult.top_risks.length > 0 && (
            <div className="top-risks-section">
              <h3>🔴 Top Security Risks</h3>
              <div className="risks-list">
                {scanResult.top_risks.map((risk, index) => (
                  <div key={index} className={`risk-item ${risk.severity.toLowerCase()}`}>
                    <div className="risk-header">
                      <span className="risk-severity">{risk.severity}</span>
                      <span className="risk-category">{risk.category}</span>
                      <span className="risk-points">+{risk.points} pts</span>
                    </div>
                    <p className="risk-issue">{risk.issue}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* OWASP Top 10 Compliance */}
          {scanResult.owasp_assessment && (
            <div className="owasp-section">
              <h3>🛡️ OWASP Top 10 Compliance</h3>
              <div className="owasp-summary">
                <p>
                  <strong>Compliance Score:</strong> {scanResult.owasp_compliance_score}/100
                </p>
                <p>
                  <strong>Compliant Categories:</strong> {scanResult.compliant_categories} / 
                  {scanResult.compliant_categories + scanResult.non_compliant_categories}
                </p>
              </div>
              {scanResult.owasp_assessment.findings && (
                <div className="owasp-findings">
                  {Object.entries(scanResult.owasp_assessment.findings).map(([key, finding]) => (
                    <div key={key} className={`owasp-item ${finding.compliant ? 'compliant' : 'non-compliant'}`}>
                      <h4>{finding.title}</h4>
                      <p className="owasp-status">
                        {finding.compliant ? '✅ Compliant' : '❌ Non-Compliant'}
                      </p>
                      <p className="owasp-description">{finding.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Recommendations */}
          {scanResult.recommendations && scanResult.recommendations.length > 0 && (
            <div className="recommendations-section">
              <h3>💡 Security Recommendations</h3>
              <ul className="recommendations-list">
                {scanResult.recommendations.map((rec, index) => (
                  <li key={index} className="recommendation-item">{rec}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Detailed Scan Results (Expandable) */}
          <details className="detailed-results">
            <summary>📋 Detailed Technical Results</summary>
            <div className="technical-details">
              <pre>{JSON.stringify(scanResult, null, 2)}</pre>
            </div>
          </details>
        </div>
      )}

      {/* Educational Footer */}
      <div className="educational-footer">
        <h4>🎓 Educational Purpose</h4>
        <p>
          This scanner performs <strong>passive, non-intrusive</strong> security checks including:
        </p>
        <ul>
          <li>HTTP Security Headers Analysis (public information)</li>
          <li>SSL/TLS Configuration Check (handshake only)</li>
          <li>DNS Security Records (public DNS lookup)</li>
          <li>Technology Fingerprinting (response analysis)</li>
          <li>OWASP Top 10 Educational Assessment</li>
        </ul>
        <p className="ethical-note">
          <strong>⚠️ Ethical Use Only:</strong> This tool is for educational and authorized security
          assessments only. Always obtain permission before scanning any website.
        </p>
      </div>
    </div>
  );
};

export default WebsiteScanner;
