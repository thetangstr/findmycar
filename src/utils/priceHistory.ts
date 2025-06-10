import { Vehicle } from '@/types';

export interface PriceHistoryEntry {
  date: string;
  price: number;
}

export interface VehiclePriceHistory {
  vehicleId: string;
  history: PriceHistoryEntry[];
}

/**
 * Utility for tracking and managing vehicle price history
 */
export const PriceHistoryService = {
  /**
   * Get price history for a specific vehicle
   * @param vehicleId - The ID of the vehicle
   * @returns Array of price history entries
   */
  getVehiclePriceHistory(vehicleId: string): PriceHistoryEntry[] {
    try {
      const storedHistories = localStorage.getItem('price_histories');
      if (!storedHistories) return [];
      
      const histories: VehiclePriceHistory[] = JSON.parse(storedHistories);
      const vehicleHistory = histories.find(h => h.vehicleId === vehicleId);
      
      return vehicleHistory?.history || [];
    } catch (error) {
      console.error('Error retrieving price history:', error);
      return [];
    }
  },
  
  /**
   * Update price history for a vehicle
   * @param vehicle - The vehicle object with current price
   */
  updatePriceHistory(vehicle: Vehicle): void {
    try {
      const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
      const storedHistories = localStorage.getItem('price_histories');
      let histories: VehiclePriceHistory[] = storedHistories ? JSON.parse(storedHistories) : [];
      
      // Find existing history for this vehicle
      let vehicleHistory = histories.find(h => h.vehicleId === vehicle.id);
      
      if (!vehicleHistory) {
        // Create new history if none exists
        vehicleHistory = {
          vehicleId: vehicle.id,
          history: []
        };
        histories.push(vehicleHistory);
      }
      
      // Check if we already have an entry for today
      const todayEntry = vehicleHistory.history.find(entry => entry.date === today);
      
      if (todayEntry) {
        // Update today's entry if price changed
        if (todayEntry.price !== vehicle.price) {
          todayEntry.price = vehicle.price;
        }
      } else {
        // Add new entry for today
        vehicleHistory.history.push({
          date: today,
          price: vehicle.price
        });
      }
      
      // Sort history by date (oldest first)
      vehicleHistory.history.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      
      // Limit history to last 90 days
      const ninetyDaysAgo = new Date();
      ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);
      const ninetyDaysAgoStr = ninetyDaysAgo.toISOString().split('T')[0];
      
      vehicleHistory.history = vehicleHistory.history.filter(entry => entry.date >= ninetyDaysAgoStr);
      
      // Save updated histories
      localStorage.setItem('price_histories', JSON.stringify(histories));
    } catch (error) {
      console.error('Error updating price history:', error);
    }
  },
  
  /**
   * Generate mock price history for demo purposes
   * @param vehicleId - The ID of the vehicle
   * @param currentPrice - The current price of the vehicle
   * @param days - Number of days of history to generate
   * @returns Array of price history entries
   */
  generateMockPriceHistory(vehicleId: string, currentPrice: number, days: number = 60): PriceHistoryEntry[] {
    const history: PriceHistoryEntry[] = [];
    const today = new Date();
    
    // Generate random price fluctuations
    let price = currentPrice;
    
    for (let i = days; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      // Random price change (between -2% and +1%)
      const changePercent = Math.random() * 3 - 2;
      price = Math.round(price * (1 + changePercent / 100));
      
      // Ensure price doesn't go below 50% or above 120% of current price
      const minPrice = currentPrice * 0.5;
      const maxPrice = currentPrice * 1.2;
      price = Math.max(minPrice, Math.min(maxPrice, price));
      
      // Only add an entry every few days to make it more realistic
      if (i === 0 || i === days || Math.random() < 0.3) {
        history.push({
          date: date.toISOString().split('T')[0],
          price
        });
      }
    }
    
    // Ensure the last entry matches the current price
    if (history.length > 0) {
      history[history.length - 1].price = currentPrice;
    }
    
    return history;
  }
};

export default PriceHistoryService;
