// Enhanced Search Demo JavaScript
// Overrides the search functionality to work with the demo

document.addEventListener('DOMContentLoaded', function() {
    // Override the performEnhancedSearch method
    if (window.enhancedSearch) {
        window.enhancedSearch.performEnhancedSearch = async function() {
            const query = this.searchInput.value.trim().toLowerCase();
            if (!query && !this.hasActiveFilters()) {
                return;
            }
            
            // Add to search history
            this.addToSearchHistory(query);
            
            // Show loading state
            this.showLoadingState();
            
            // Simulate API delay
            setTimeout(() => {
                // Filter demo vehicles based on query
                const filteredVehicles = this.filterVehicles(query);
                
                // Update the results grid
                this.updateResultsGrid(filteredVehicles);
                
                // Hide loading state
                this.hideLoadingState();
                
                // Update results count
                this.updateResultsCount(filteredVehicles.length);
            }, 1000);
        };
        
        // Add helper method to check for active filters
        window.enhancedSearch.hasActiveFilters = function() {
            const filters = this.collectFilters();
            return Object.values(filters).some(value => value !== null && value !== '');
        };
        
        // Add method to filter vehicles
        window.enhancedSearch.filterVehicles = function(query) {
            // Get all vehicles from the page
            let vehicles = window.demoVehicles || [];
            
            // Filter based on query
            if (query) {
                vehicles = vehicles.filter(v => {
                    const searchText = `${v.make} ${v.model} ${v.title} ${v.year}`.toLowerCase();
                    return searchText.includes(query);
                });
            }
            
            // Apply filters
            const filters = this.collectFilters();
            
            if (filters.price_min) {
                vehicles = vehicles.filter(v => v.price >= parseInt(filters.price_min));
            }
            if (filters.price_max) {
                vehicles = vehicles.filter(v => v.price <= parseInt(filters.price_max));
            }
            if (filters.mileage_max) {
                vehicles = vehicles.filter(v => v.mileage <= parseInt(filters.mileage_max));
            }
            if (filters.year_min) {
                vehicles = vehicles.filter(v => v.year >= parseInt(filters.year_min));
            }
            if (filters.year_max) {
                vehicles = vehicles.filter(v => v.year <= parseInt(filters.year_max));
            }
            
            return vehicles;
        };
        
        // Add method to update results grid
        window.enhancedSearch.updateResultsGrid = function(vehicles) {
            const resultsGrid = document.querySelector('.results-grid');
            if (!resultsGrid) return;
            
            if (vehicles.length === 0) {
                resultsGrid.innerHTML = `
                    <div class="col-12 text-center py-5">
                        <i class="fas fa-search fa-3x text-muted mb-3"></i>
                        <h4>No vehicles found</h4>
                        <p class="text-muted">Try adjusting your search criteria or filters</p>
                    </div>
                `;
                return;
            }
            
            resultsGrid.innerHTML = vehicles.map(vehicle => `
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="vehicle-card">
                        <a href="/vehicle/${vehicle.id}" class="text-decoration-none">
                            <img src="${vehicle.image_url}" alt="${vehicle.title}" class="vehicle-image">
                        </a>
                        <div class="vehicle-info">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h5 class="vehicle-title">${vehicle.title}</h5>
                                <button class="btn btn-sm btn-outline-danger favorite-btn" 
                                        onclick="toggleFavorite(${vehicle.id})" 
                                        title="Add to favorites">
                                    <i class="far fa-heart"></i>
                                </button>
                            </div>
                            
                            <div class="vehicle-price">
                                $${vehicle.price.toLocaleString()}
                                ${vehicle.deal_rating ? `<span class="badge badge-success ml-2">${vehicle.deal_rating}</span>` : ''}
                            </div>
                            
                            <div class="vehicle-details">
                                <span><i class="fas fa-tachometer-alt"></i> ${vehicle.mileage.toLocaleString()} mi</span>
                                <span><i class="fas fa-map-marker-alt"></i> ${vehicle.location}</span>
                            </div>
                            
                            <div class="vehicle-meta">
                                <span class="source-badge ${vehicle.source}">${vehicle.source}</span>
                                ${vehicle.estimated_value ? `<span class="estimated-value">Est. Value: $${vehicle.estimated_value.toLocaleString()}</span>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        };
        
        // Add method to update results count
        window.enhancedSearch.updateResultsCount = function(count) {
            const countElement = document.querySelector('.results-count');
            if (countElement) {
                countElement.textContent = `${count} vehicles found`;
            }
        };
        
        // Also handle the quick search tags
        document.querySelectorAll('.quick-tag').forEach(tag => {
            tag.addEventListener('click', (e) => {
                e.preventDefault();
                const query = tag.getAttribute('data-query');
                window.enhancedSearch.searchInput.value = query;
                window.enhancedSearch.performEnhancedSearch();
            });
        });
        
        // Handle search form submission
        const searchForm = document.querySelector('.search-container form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                window.enhancedSearch.performEnhancedSearch();
            });
        }
    }
});