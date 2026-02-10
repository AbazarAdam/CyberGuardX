/**
 * CyberGuardX Website Scanner - Real-Time Progress Component
 * Displays animated progress with step-by-step updates
 */

class ScanProgressTracker {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scanId = null;
        this.pollInterval = null;
        this.isComplete = false;
        this.progressData = null;
    }

    /**
     * Start tracking a scan's progress
     */
    startTracking(scanId, url) {
        this.scanId = scanId;
        this.isComplete = false;
        this.render(url);
        this.startPolling();
    }

    /**
     * Render the initial progress UI
     */
    render(url) {
        this.container.innerHTML = `
            <div class="progress-container">
                <div class="progress-header">
                    <h3>🔍 Scanning: ${this.escapeHtml(url)}</h3>
                    <button id="cancel-scan-btn" class="btn-cancel">✖ Cancel</button>
                </div>
                
                <div class="progress-main">
                    <!-- Progress Bar -->
                    <div class="progress-wrapper">
                        <div class="progress-bar-container">
                            <div id="progress-bar-fill" class="progress-bar-fill" style="width: 0%">
                                <span id="progress-percentage" class="progress-percentage">0%</span>
                            </div>
                        </div>
                        <div id="progress-label" class="progress-label">Initializing...</div>
                    </div>
                    
                    <!-- Time Information -->
                    <div class="progress-time">
                        <div class="time-item">
                            <span class="time-icon">⏱️</span>
                            <span id="time-elapsed">00:00:00</span>
                            <span class="time-sublabel">Elapsed</span>
                        </div>
                        <div class="time-item">
                            <span class="time-icon">⏳</span>
                            <span id="time-remaining">--:--:--</span>
                            <span class="time-sublabel">Remaining</span>
                        </div>
                    </div>
                    
                    <!-- Step Checklist -->
                    <div class="progress-steps">
                        <div class="step-item" data-step="1">
                            <span class="step-icon">◯</span>
                            <span class="step-name">Validating URL and permissions</span>
                        </div>
                        <div class="step-item" data-step="2">
                            <span class="step-icon">◯</span>
                            <span class="step-name">Checking HTTP Security Headers</span>
                        </div>
                        <div class="step-item" data-step="3">
                            <span class="step-icon">◯</span>
                            <span class="step-name">Analyzing SSL/TLS Configuration</span>
                        </div>
                        <div class="step-item" data-step="4">
                            <span class="step-icon">◯</span>
                            <span class="step-name">Scanning DNS Security Records</span>
                        </div>
                        <div class="step-item" data-step="5">
                            <span class="step-icon">◯</span>
                            <span class="step-name">Detecting Technology Stack</span>
                        </div>
                        <div class="step-item" data-step="6">
                            <span class="step-icon">◯</span>
                            <span class="step-name">Calculating Risk Score</span>
                        </div>
                        <div class="step-item" data-step="7">
                            <span class="step-icon">◯</span>
                            <span class="step-name">Generating Comprehensive Report</span>
                        </div>
                    </div>
                    
                    <!-- Sub-steps -->
                    <div id="substeps-container" class="substeps-container"></div>
                </div>
            </div>
        `;

        // Add cancel button listener
        document.getElementById('cancel-scan-btn')?.addEventListener('click', () => this.cancelScan());
    }

    /**
     * Start polling for progress updates
     */
    startPolling() {
        this.pollInterval = setInterval(() => this.fetchProgress(), 2000); // Poll every 2 seconds
        this.fetchProgress(); // Immediate first fetch
    }

    /**
     * Fetch progress from API
     */
    async fetchProgress() {
        if (!this.scanId) return;

        try {
            const response = await fetch(`${API_BASE_URL}/scan-progress/${this.scanId}`);
            
            if (!response.ok) {
                throw new Error(`Progress fetch failed: ${response.status}`);
            }

            const data = await response.json();
            this.progressData = data;
            this.updateUI(data);

            // Stop polling if complete or error
            if (data.is_complete || data.has_error || data.is_cancelled) {
                this.stopPolling();
                this.isComplete = true;
                this.showCompletionState(data);
            }
        } catch (error) {
            console.error('Error fetching progress:', error);
        }
    }

    /**
     * Update UI with progress data
     */
    updateUI(data) {
        // Update progress bar
        const progressBar = document.getElementById('progress-bar-fill');
        const progressPercentage = document.getElementById('progress-percentage');
        const progressLabel = document.getElementById('progress-label');

        if (progressBar) {
            progressBar.style.width = `${data.progress_percentage}%`;
            
            // Color based on percentage
            if (data.progress_percentage < 30) {
                progressBar.style.background = 'linear-gradient(90deg, #00f3ff, #0099ff)';
            } else if (data.progress_percentage < 70) {
                progressBar.style.background = 'linear-gradient(90deg, #0099ff, #00cc99)';
            } else {
                progressBar.style.background = 'linear-gradient(90deg, #00cc99, #00ff9d)';
            }
        }

        if (progressPercentage) {
            progressPercentage.textContent = `${data.progress_percentage}%`;
        }

        if (progressLabel) {
            progressLabel.textContent = data.current_step;
        }

        // Update time displays
        document.getElementById('time-elapsed').textContent = data.time_elapsed || '00:00:00';
        document.getElementById('time-remaining').textContent = data.estimated_remaining || '--:--:--';

        // Update step indicators
        this.updateSteps(data);

        // Update substeps
        this.updateSubsteps(data.step_details);
    }

    /**
     * Update step indicators
     */
    updateSteps(data) {
        const steps = document.querySelectorAll('.step-item');
        const currentStepNumber = this.getStepNumber(data.current_step);

        steps.forEach((step, index) => {
            const stepNum = index + 1;
            const icon = step.querySelector('.step-icon');

            step.classList.remove('completed', 'current', 'pending');

            if (stepNum < currentStepNumber) {
                // Completed
                step.classList.add('completed');
                icon.textContent = '✓';
            } else if (stepNum === currentStepNumber) {
                // Current
                step.classList.add('current');
                icon.textContent = '◉';
            } else {
                // Pending
                step.classList.add('pending');
                icon.textContent = '◯';
            }
        });
    }

    /**
     * Update substeps display
     */
    updateSubsteps(stepDetails) {
        const container = document.getElementById('substeps-container');
        if (!container || !stepDetails) return;

        const { completed, current, remaining } = stepDetails;

        let html = '<div class="substeps-list">';
        
        // Completed substeps
        if (completed && completed.length > 0) {
            completed.forEach(substep => {
                html += `
                    <div class="substep-item completed">
                        <span class="substep-icon">✓</span>
                        <span class="substep-name">${this.escapeHtml(substep)}</span>
                    </div>
                `;
            });
        }

        // Current substep
        if (current) {
            html += `
                <div class="substep-item current">
                    <span class="substep-icon pulse">⟳</span>
                    <span class="substep-name">${this.escapeHtml(current)}</span>
                </div>
            `;
        }

        // Remaining substeps
        if (remaining && remaining.length > 0) {
            remaining.forEach(substep => {
                html += `
                    <div class="substep-item pending">
                        <span class="substep-icon">◯</span>
                        <span class="substep-name">${this.escapeHtml(substep)}</span>
                    </div>
                `;
            });
        }

        html += '</div>';
        container.innerHTML = html;
    }

    /**
     * Show completion state
     */
    showCompletionState(data) {
        const container = this.container.querySelector('.progress-container');

        if (data.has_error) {
            container.classList.add('error');
            document.getElementById('progress-label').textContent = `❌ Error: ${data.error_message}`;
        } else if (data.is_cancelled) {
            container.classList.add('cancelled');
            document.getElementById('progress-label').textContent = '⚠️ Scan cancelled by user';
        } else if (data.is_complete) {
            container.classList.add('complete');
            document.getElementById('progress-label').textContent = '✅ Scan complete!';
            
            // Hide cancel button
            const cancelBtn = document.getElementById('cancel-scan-btn');
            if (cancelBtn) cancelBtn.style.display = 'none';
        }
    }

    /**
     * Cancel  the scan
     */
    async cancelScan() {
        if (!this.scanId) return;

        const confirmed = confirm('Are you sure you want to cancel this scan?');
        if (!confirmed) return;

        try {
            const response = await fetch(`${API_BASE_URL}/scan-progress/${this.scanId}/cancel`, {
                method: 'POST'
            });

            if (response.ok) {
                this.stopPolling();
                document.getElementById('progress-label').textContent = '⚠️ Cancelling scan...';
            }
        } catch (error) {
            console.error('Error cancelling scan:', error);
            alert('Failed to cancel scan');
        }
    }

    /**
     * Stop polling
     */
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    /**
     * Get step number from step name
     */
    getStepNumber(stepName) {
        const steps = [
            'Validating URL and permissions',
            'Checking HTTP Security Headers',
            'Analyzing SSL/TLS Configuration',
            'Scanning DNS Security Records',
            'Detecting Technology Stack',
            'Calculating Risk Score',
            'Generating Comprehensive Report',
            'Complete'
        ];

        const index = steps.findIndex(s => stepName.includes(s) || s.includes(stepName));
        return index >= 0 ? index + 1 : 1;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Cleanup
     */
    destroy() {
        this.stopPolling();
        this.container.innerHTML = '';
    }
}
