// Enhanced Search JavaScript

class EnhancedSearch {
    constructor() {
        this.searchInput = document.getElementById('query');
        this.suggestionsContainer = document.getElementById('searchSuggestions');
        this.priceMinSlider = document.getElementById('priceMin');
        this.priceMaxSlider = document.getElementById('priceMax');
        this.mileageMaxSlider = document.getElementById('mileageMax');
        this.yearMinSlider = document.getElementById('yearMin');
        this.yearMaxSlider = document.getElementById('yearMax');
        this.searchHistory = JSON.parse(localStorage.getItem('searchHistory')) || [];
        
        this.initializeEventListeners();
        this.initializePriceSliders();
        this.initializeMileageSlider();
        this.initializeYearSliders();
        this.loadSearchHistory();
    }

    initializeEventListeners() {
        // Search input with suggestions
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.handleSearchInput(e.target.value);
            });

            this.searchInput.addEventListener('focus', () => {
                this.showSearchHistory();
            });

            this.searchInput.addEventListener('blur', () => {
                // Delay hiding suggestions to allow clicking
                setTimeout(() => {
                    this.hideSuggestions();
                }, 200);
            });
        }

        // Quick search tags
        document.querySelectorAll('.quick-tag').forEach(tag => {
            tag.addEventListener('click', (e) => {
                const searchText = e.target.textContent.trim();
                this.performQuickSearch(searchText);
            });
        });

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.toggleFilterButton(e.target);
            });
        });

        // Clear filters button
        const clearFiltersBtn = document.getElementById('clearFilters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearAllFilters();
            });
        }

        // Enhanced form submission
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performEnhancedSearch();
            });
        }
    }

    initializePriceSliders() {
        if (!this.priceMinSlider || !this.priceMaxSlider) return;

        const updatePriceDisplay = () => {
            const minVal = parseInt(this.priceMinSlider.value);
            const maxVal = parseInt(this.priceMaxSlider.value);
            
            // Ensure min doesn't exceed max
            if (minVal > maxVal) {
                this.priceMinSlider.value = maxVal;
            }
            
            document.getElementById('priceMinValue').textContent = 
                '$' + parseInt(this.priceMinSlider.value).toLocaleString();
            document.getElementById('priceMaxValue').textContent = 
                '$' + parseInt(this.priceMaxSlider.value).toLocaleString();
        };

        this.priceMinSlider.addEventListener('input', updatePriceDisplay);
        this.priceMaxSlider.addEventListener('input', updatePriceDisplay);
        
        // Initialize display
        updatePriceDisplay();
    }

    initializeMileageSlider() {
        if (!this.mileageMaxSlider) return;

        const updateMileageDisplay = () => {
            const maxVal = parseInt(this.mileageMaxSlider.value);
            document.getElementById('mileageMaxValue').textContent = 
                maxVal.toLocaleString() + ' miles';
        };

        this.mileageMaxSlider.addEventListener('input', updateMileageDisplay);
        updateMileageDisplay();
    }

    initializeYearSliders() {
        if (!this.yearMinSlider || !this.yearMaxSlider) return;

        const updateYearDisplay = () => {
            const minVal = parseInt(this.yearMinSlider.value);
            const maxVal = parseInt(this.yearMaxSlider.value);
            
            // Ensure min doesn't exceed max
            if (minVal > maxVal) {
                this.yearMinSlider.value = maxVal;
            }
            
            document.getElementById('yearMinValue').textContent = this.yearMinSlider.value;
            document.getElementById('yearMaxValue').textContent = this.yearMaxSlider.value;
        };

        this.yearMinSlider.addEventListener('input', updateYearDisplay);
        this.yearMaxSlider.addEventListener('input', updateYearDisplay);
        
        // Initialize display
        updateYearDisplay();
    }

    handleSearchInput(query) {
        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }

        this.showSuggestions(this.generateSuggestions(query));
    }

    generateSuggestions(query) {
        const suggestions = [];
        const lowerQuery = query.toLowerCase();

        // Popular makes and models
        const popularCars = [
            { text: 'Honda Civic', icon: 'fas fa-car' },
            { text: 'Toyota Camry', icon: 'fas fa-car' },
            { text: 'Tesla Model 3', icon: 'fas fa-bolt' },
            { text: 'Ford F-150', icon: 'fas fa-truck' },
            { text: 'BMW 3 Series', icon: 'fas fa-car' },
            { text: 'Mercedes-Benz C-Class', icon: 'fas fa-star' },
            { text: 'Audi A4', icon: 'fas fa-car' },
            { text: 'Jeep Wrangler', icon: 'fas fa-mountain' },
            { text: 'Subaru Outback', icon: 'fas fa-car' },
            { text: 'Mazda CX-5', icon: 'fas fa-car' }
        ];

        // Add matching popular cars
        popularCars.forEach(car => {
            if (car.text.toLowerCase().includes(lowerQuery)) {
                suggestions.push({
                    text: car.text,
                    icon: car.icon,
                    type: 'popular'
                });
            }
        });

        // Add price-based suggestions
        if (lowerQuery.includes('under') || lowerQuery.includes('below')) {
            suggestions.push({
                text: query + ' under $20,000',
                icon: 'fas fa-dollar-sign',
                type: 'price'
            });
            suggestions.push({
                text: query + ' under $30,000',
                icon: 'fas fa-dollar-sign',
                type: 'price'
            });
        }

        // Add use case suggestions
        const useCases = [
            { text: 'family car', icon: 'fas fa-users' },
            { text: 'luxury sedan', icon: 'fas fa-star' },
            { text: 'fuel efficient', icon: 'fas fa-leaf' },
            { text: 'sports car', icon: 'fas fa-tachometer-alt' },
            { text: 'truck', icon: 'fas fa-truck' },
            { text: 'SUV', icon: 'fas fa-car' }
        ];

        useCases.forEach(useCase => {
            if (useCase.text.toLowerCase().includes(lowerQuery)) {
                suggestions.push({
                    text: useCase.text,
                    icon: useCase.icon,
                    type: 'category'
                });
            }
        });

        return suggestions.slice(0, 8); // Limit to 8 suggestions
    }

    showSuggestions(suggestions) {
        if (!suggestions.length) {
            this.hideSuggestions();
            return;
        }

        let html = '';
        suggestions.forEach(suggestion => {
            html += `
                <div class="suggestion-item" onclick="selectSuggestion('${suggestion.text}')">
                    <i class="${suggestion.icon}"></i>
                    <span>${suggestion.text}</span>
                </div>
            `;
        });

        this.suggestionsContainer.innerHTML = html;
        this.suggestionsContainer.style.display = 'block';
    }

    hideSuggestions() {
        if (this.suggestionsContainer) {
            this.suggestionsContainer.style.display = 'none';
        }
    }

    showSearchHistory() {
        if (!this.searchHistory.length) return;

        let html = '';
        this.searchHistory.slice(0, 5).forEach(search => {
            html += `
                <div class="suggestion-item" onclick="selectSuggestion('${search}')">
                    <i class="fas fa-history"></i>
                    <span>${search}</span>
                </div>
            `;
        });

        this.suggestionsContainer.innerHTML = html;
        this.suggestionsContainer.style.display = 'block';
    }

    addToSearchHistory(query) {
        // Remove if already exists
        this.searchHistory = this.searchHistory.filter(item => item !== query);
        
        // Add to beginning
        this.searchHistory.unshift(query);
        
        // Keep only last 10 searches
        this.searchHistory = this.searchHistory.slice(0, 10);
        
        // Save to localStorage
        localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
        
        this.loadSearchHistory();
    }

    loadSearchHistory() {
        const historyContainer = document.getElementById('searchHistoryContainer');
        if (!historyContainer || !this.searchHistory.length) return;

        let html = '<h6><i class="fas fa-history"></i> Recent Searches</h6>';
        this.searchHistory.slice(0, 5).forEach(search => {
            html += `
                <div class="history-item" onclick="selectSuggestion('${search}')">
                    <span>${search}</span>
                    <i class="fas fa-times remove-history" onclick="removeFromHistory('${search}', event)"></i>
                </div>
            `;
        });

        historyContainer.innerHTML = html;
    }

    removeFromHistory(query, event) {
        event.stopPropagation();
        this.searchHistory = this.searchHistory.filter(item => item !== query);
        localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
        this.loadSearchHistory();
    }

    performQuickSearch(query) {
        this.searchInput.value = query;
        this.addToSearchHistory(query);
        this.performEnhancedSearch();
    }

    toggleFilterButton(button) {
        button.classList.toggle('active');
        this.updateFilters();
    }

    updateFilters() {
        // Get all active filter buttons
        const activeFilters = document.querySelectorAll('.filter-btn.active');
        
        // Update form fields based on active filters
        activeFilters.forEach(filter => {
            const filterType = filter.dataset.filter;
            const filterValue = filter.dataset.value;
            
            const input = document.querySelector(`[name="${filterType}"]`);
            if (input) {
                input.value = filterValue;
            }
        });
    }

    clearAllFilters() {
        // Clear all filter buttons
        document.querySelectorAll('.filter-btn.active').forEach(btn => {
            btn.classList.remove('active');
        });

        // Reset all sliders
        if (this.priceMinSlider) this.priceMinSlider.value = 0;
        if (this.priceMaxSlider) this.priceMaxSlider.value = 100000;
        if (this.mileageMaxSlider) this.mileageMaxSlider.value = 200000;
        if (this.yearMinSlider) this.yearMinSlider.value = 1990;
        if (this.yearMaxSlider) this.yearMaxSlider.value = 2024;

        // Reset form fields
        const form = document.getElementById('searchForm');
        if (form) {
            const inputs = form.querySelectorAll('input[type="text"], select');
            inputs.forEach(input => {
                if (input.id !== 'query') {
                    input.value = '';
                }
            });
        }

        // Update displays
        this.initializePriceSliders();
        this.initializeMileageSlider();
        this.initializeYearSliders();
    }

    performEnhancedSearch() {
        const query = this.searchInput.value.trim();
        if (!query) return;

        // Add to search history
        this.addToSearchHistory(query);

        // Show loading state
        this.showLoadingState();

        // Collect all filter values
        const filters = this.collectFilters();

        // Submit form with enhanced data
        const formData = new FormData();
        formData.append('query', query);
        
        // Add all filter values
        Object.keys(filters).forEach(key => {
            if (filters[key]) {
                formData.append(key, filters[key]);
            }
        });

        // Submit the form
        fetch('/ingest', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(html => {
            // Replace page content with results
            document.body.innerHTML = html;
            
            // Reinitialize search functionality
            new EnhancedSearch();
        })
        .catch(error => {
            console.error('Search error:', error);
            this.hideLoadingState();
        });
    }

    collectFilters() {
        const filters = {};

        // Price range
        if (this.priceMinSlider && this.priceMaxSlider) {
            filters.price_min = this.priceMinSlider.value;
            filters.price_max = this.priceMaxSlider.value;
        }

        // Mileage
        if (this.mileageMaxSlider) {
            filters.mileage_max = this.mileageMaxSlider.value;
        }

        // Year range
        if (this.yearMinSlider && this.yearMaxSlider) {
            filters.year_min = this.yearMinSlider.value;
            filters.year_max = this.yearMaxSlider.value;
        }

        // Other form fields
        const form = document.getElementById('searchForm');
        if (form) {
            const inputs = form.querySelectorAll('input[type="text"], select');
            inputs.forEach(input => {
                if (input.value && input.name && input.name !== 'query') {
                    filters[input.name] = input.value;
                }
            });
        }

        // Active filter buttons
        document.querySelectorAll('.filter-btn.active').forEach(btn => {
            const filterType = btn.dataset.filter;
            const filterValue = btn.dataset.value;
            if (filterType && filterValue) {
                filters[filterType] = filterValue;
            }
        });

        return filters;
    }

    showLoadingState() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'block';
        }
    }

    hideLoadingState() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
}

// Global functions for onclick handlers
function selectSuggestion(text) {
    document.getElementById('query').value = text;
    document.getElementById('searchSuggestions').style.display = 'none';
    
    // Trigger search
    const searchInstance = window.enhancedSearch;
    if (searchInstance) {
        searchInstance.performEnhancedSearch();
    }
}

function removeFromHistory(query, event) {
    const searchInstance = window.enhancedSearch;
    if (searchInstance) {
        searchInstance.removeFromHistory(query, event);
    }
}

// Initialize enhanced search when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.enhancedSearch = new EnhancedSearch();
});

// Search suggestions data
const searchSuggestions = {
    makes: [
        'Honda', 'Toyota', 'Ford', 'Chevrolet', 'BMW', 'Mercedes-Benz', 
        'Audi', 'Volkswagen', 'Nissan', 'Hyundai', 'Kia', 'Mazda', 
        'Subaru', 'Lexus', 'Acura', 'Infiniti', 'Cadillac', 'Lincoln',
        'Jeep', 'Ram', 'GMC', 'Buick', 'Chrysler', 'Dodge', 'Tesla',
        'Porsche', 'Jaguar', 'Land Rover', 'Volvo', 'Mini', 'Fiat'
    ],
    models: {
        'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot', 'Odyssey', 'Fit', 'HR-V'],
        'Toyota': ['Camry', 'Corolla', 'RAV4', 'Prius', 'Highlander', 'Sienna', 'Tacoma'],
        'Ford': ['F-150', 'Mustang', 'Explorer', 'Escape', 'Focus', 'Fusion', 'Edge'],
        'Chevrolet': ['Silverado', 'Malibu', 'Equinox', 'Tahoe', 'Camaro', 'Cruze', 'Traverse'],
        'BMW': ['3 Series', '5 Series', 'X3', 'X5', 'X1', '7 Series', 'i3'],
        'Mercedes-Benz': ['C-Class', 'E-Class', 'S-Class', 'GLC', 'GLE', 'A-Class', 'CLA'],
        'Tesla': ['Model 3', 'Model Y', 'Model S', 'Model X', 'Cybertruck']
    },
    categories: [
        'sedan', 'SUV', 'truck', 'coupe', 'convertible', 'hatchback', 
        'wagon', 'pickup', 'minivan', 'crossover', 'sports car', 
        'luxury car', 'electric car', 'hybrid', 'diesel'
    ],
    priceRanges: [
        'under $10,000', 'under $15,000', 'under $20,000', 'under $25,000',
        'under $30,000', 'under $40,000', 'under $50,000', '$50,000-$75,000',
        '$75,000-$100,000', 'over $100,000'
    ]
};