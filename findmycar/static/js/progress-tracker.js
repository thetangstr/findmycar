/**
 * Enhanced progress tracking for search operations
 */

class SearchProgressTracker {
    constructor() {
        this.startTime = null;
        this.sources = [];
        this.completedSources = [];
        this.progressInterval = null;
    }

    start(sources) {
        this.startTime = Date.now();
        this.sources = sources;
        this.completedSources = [];
        
        // Update the loading overlay with progress information
        this.updateLoadingOverlay();
        
        // Start progress animation
        this.progressInterval = setInterval(() => {
            this.updateProgress();
        }, 100);
    }

    updateLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (!overlay) return;

        const content = overlay.querySelector('.text-center');
        if (!content) return;

        // Create enhanced progress display
        content.innerHTML = `
            <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                <span class="sr-only">Loading...</span>
            </div>
            <h4 class="mt-3 mb-3">Searching for vehicles...</h4>
            <div class="progress mb-3" style="width: 300px; margin: 0 auto;">
                <div id="searchProgress" class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" style="width: 0%"></div>
            </div>
            <p class="mb-2">Searching across ${this.sources.length} sources:</p>
            <div id="sourceStatus" class="text-left" style="max-width: 400px; margin: 0 auto;">
                ${this.sources.map(source => `
                    <div class="source-item mb-1" data-source="${source}">
                        <i class="fas fa-circle-notch fa-spin text-warning"></i>
                        <span class="ml-2">${this.formatSourceName(source)}</span>
                        <span class="float-right text-muted">Searching...</span>
                    </div>
                `).join('')}
            </div>
            <div class="mt-3">
                <small class="text-muted">Elapsed: <span id="elapsedTime">0s</span></small>
            </div>
        `;
    }

    updateProgress() {
        // Update elapsed time
        const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
        const elapsedElement = document.getElementById('elapsedTime');
        if (elapsedElement) {
            elapsedElement.textContent = `${elapsed}s`;
        }

        // Update progress bar (estimate based on time and typical search duration)
        const progressBar = document.getElementById('searchProgress');
        if (progressBar) {
            const estimatedDuration = 10; // seconds
            const progress = Math.min(95, (elapsed / estimatedDuration) * 100);
            progressBar.style.width = `${progress}%`;
        }

        // Simulate source completion (in real implementation, this would be updated via WebSocket or SSE)
        this.simulateSourceCompletion(elapsed);
    }

    simulateSourceCompletion(elapsed) {
        // Simulate sources completing at different times
        const completionTimes = {
            'ebay': 2,
            'carmax': 3,
            'autotrader': 4,
            'bringatrailer': 5,
            'cargurus': 6
        };

        this.sources.forEach(source => {
            if (!this.completedSources.includes(source) && elapsed >= (completionTimes[source] || 3)) {
                this.markSourceComplete(source, Math.floor(Math.random() * 20) + 5);
            }
        });
    }

    markSourceComplete(source, vehicleCount = 0) {
        if (this.completedSources.includes(source)) return;
        
        this.completedSources.push(source);
        
        const sourceElement = document.querySelector(`[data-source="${source}"]`);
        if (sourceElement) {
            sourceElement.innerHTML = `
                <i class="fas fa-check-circle text-success"></i>
                <span class="ml-2">${this.formatSourceName(source)}</span>
                <span class="float-right text-success">${vehicleCount} vehicles</span>
            `;
        }

        // Update progress bar
        const progress = (this.completedSources.length / this.sources.length) * 100;
        const progressBar = document.getElementById('searchProgress');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }

        // Check if all sources are complete
        if (this.completedSources.length === this.sources.length) {
            this.complete();
        }
    }

    formatSourceName(source) {
        const names = {
            'ebay': 'eBay Motors',
            'carmax': 'CarMax',
            'autotrader': 'Autotrader',
            'bringatrailer': 'Bring a Trailer',
            'cargurus': 'CarGurus'
        };
        return names[source] || source;
    }

    complete() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        // Update UI to show completion
        const progressBar = document.getElementById('searchProgress');
        if (progressBar) {
            progressBar.style.width = '100%';
            progressBar.classList.remove('progress-bar-animated');
        }

        // Hide overlay after a short delay
        setTimeout(() => {
            document.getElementById('loadingOverlay').style.display = 'none';
        }, 500);
    }
}

// Create global instance
window.searchProgressTracker = new SearchProgressTracker();