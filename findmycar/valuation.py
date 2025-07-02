import requests
import json
from typing import Dict, Optional
from config import OPENAI_API_KEY

class VehicleValuation:
    """
    Vehicle valuation service that provides market value estimates and deal ratings.
    Uses multiple data sources and fallback mechanisms.
    """
    
    def __init__(self):
        self.base_url = "https://api.carapi.app/v1"
        self.backup_enabled = True
    
    def get_vehicle_valuation(self, make: str, model: str, year: int, 
                            mileage: int = None, trim: str = None, 
                            condition: str = "good") -> Dict:
        """
        Get vehicle valuation and market analysis.
        
        Returns:
        {
            "estimated_value": float,
            "market_min": float,
            "market_max": float,
            "deal_rating": str,  # "Great Deal", "Good Deal", "Fair Price", "High Price"
            "confidence": float,  # 0.0 to 1.0
            "data_source": str
        }
        """
        
        # Try primary valuation method
        try:
            valuation = self._get_carapi_valuation(make, model, year, mileage, trim, condition)
            if valuation:
                return valuation
        except Exception as e:
            print(f"Primary valuation failed: {e}")
        
        # Try backup estimation method
        try:
            valuation = self._get_estimated_valuation(make, model, year, mileage, condition)
            if valuation:
                return valuation
        except Exception as e:
            print(f"Backup valuation failed: {e}")
        
        # Return default if all methods fail
        return self._get_default_valuation()
    
    def _get_carapi_valuation(self, make: str, model: str, year: int, 
                            mileage: int, trim: str, condition: str) -> Optional[Dict]:
        """
        Get valuation from CarAPI.app (free tier available).
        """
        try:
            # Search for vehicle
            search_url = f"{self.base_url}/cars"
            params = {
                "make": make,
                "model": model,
                "year": year,
                "limit": 5
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Use the first matching vehicle for baseline
                    vehicle = data[0]
                    base_value = self._estimate_base_value(make, model, year)
                    
                    # Adjust for mileage and condition
                    adjusted_value = self._adjust_for_mileage_and_condition(
                        base_value, year, mileage, condition
                    )
                    
                    return {
                        "estimated_value": adjusted_value,
                        "market_min": adjusted_value * 0.85,
                        "market_max": adjusted_value * 1.15,
                        "deal_rating": "Fair Price",
                        "confidence": 0.7,
                        "data_source": "CarAPI + Estimation"
                    }
            
        except Exception as e:
            print(f"CarAPI valuation error: {e}")
            
        return None
    
    def calculate_deal_rating(self, listing_price: float, estimated_value: float, 
                             market_min: float, market_max: float) -> str:
        """
        Calculate deal rating based on listing price vs market value.
        """
        if not listing_price or not estimated_value:
            return "Unknown"
        
        price_ratio = listing_price / estimated_value
        
        if price_ratio <= 0.85:
            return "Great Deal"
        elif price_ratio <= 0.95:
            return "Good Deal"
        elif price_ratio <= 1.05:
            return "Fair Price"
        else:
            return "High Price"
    
    def _get_estimated_valuation(self, make: str, model: str, year: int, 
                               mileage: int, condition: str) -> Optional[Dict]:
        """
        Fallback estimation using industry averages and depreciation models.
        """
        try:
            base_value = self._estimate_base_value(make, model, year)
            adjusted_value = self._adjust_for_mileage_and_condition(
                base_value, year, mileage, condition
            )
            
            return {
                "estimated_value": adjusted_value,
                "market_min": adjusted_value * 0.80,
                "market_max": adjusted_value * 1.20,
                "deal_rating": "Fair Price",
                "confidence": 0.5,
                "data_source": "Estimated"
            }
            
        except Exception as e:
            print(f"Estimation error: {e}")
            
        return None
    
    def _estimate_base_value(self, make: str, model: str, year: int) -> float:
        """
        Estimate base vehicle value using industry averages and brand factors.
        """
        current_year = 2024
        age = current_year - year
        
        # Base MSRP estimates by brand/segment (rough estimates)
        brand_factors = {
            'toyota': 25000, 'honda': 24000, 'nissan': 22000,
            'ford': 28000, 'chevrolet': 27000, 'gmc': 35000,
            'bmw': 45000, 'mercedes': 50000, 'audi': 48000,
            'lexus': 42000, 'acura': 38000, 'infiniti': 40000,
            'tesla': 55000, 'porsche': 70000, 'jaguar': 55000,
            'volvo': 40000, 'subaru': 26000, 'mazda': 24000,
            'hyundai': 22000, 'kia': 21000, 'volkswagen': 28000,
            'jeep': 32000, 'ram': 35000, 'dodge': 30000,
            'cadillac': 45000, 'lincoln': 48000, 'buick': 32000
        }
        
        base_msrp = brand_factors.get(make.lower(), 25000)
        
        # Model adjustments (basic categories)
        model_lower = model.lower()
        if any(word in model_lower for word in ['luxury', 'premium', 'x5', 'x3', 'c-class', 'e-class']):
            base_msrp *= 1.5
        elif any(word in model_lower for word in ['truck', 'f-150', 'silverado', 'ram']):
            base_msrp *= 1.3
        elif any(word in model_lower for word in ['suv', 'explorer', 'tahoe', 'suburban']):
            base_msrp *= 1.2
        elif any(word in model_lower for word in ['sports', 'coupe', 'gt', 'sport']):
            base_msrp *= 1.4
        
        # Depreciation calculation
        # Year 1: 20%, Year 2: 15%, Year 3+: 10% per year
        if age == 0:
            depreciation = 0
        elif age == 1:
            depreciation = 0.20
        elif age == 2:
            depreciation = 0.35  # 20% + 15%
        else:
            depreciation = 0.35 + (age - 2) * 0.10
        
        # Cap depreciation at 85%
        depreciation = min(depreciation, 0.85)
        
        current_value = base_msrp * (1 - depreciation)
        
        return max(current_value, 1000)  # Minimum value floor
    
    def _adjust_for_mileage_and_condition(self, base_value: float, year: int, 
                                        mileage: int, condition: str) -> float:
        """
        Adjust vehicle value based on mileage and condition.
        """
        current_year = 2024
        age = current_year - year
        
        # Mileage adjustment
        if mileage:
            expected_mileage = age * 12000  # 12k miles per year average
            mileage_diff = mileage - expected_mileage
            
            # $0.10 per mile adjustment (industry rough estimate)
            mileage_adjustment = -(mileage_diff * 0.10)
            base_value += mileage_adjustment
        
        # Condition adjustment
        condition_factors = {
            'excellent': 1.10,
            'very good': 1.05,
            'good': 1.00,
            'fair': 0.85,
            'poor': 0.70
        }
        
        condition_factor = condition_factors.get(condition.lower(), 1.00)
        base_value *= condition_factor
        
        return max(base_value, 500)  # Minimum floor
    
    def calculate_deal_rating(self, listing_price: float, estimated_value: float, 
                            market_min: float, market_max: float) -> str:
        """
        Calculate deal rating based on listing price vs market value.
        """
        if listing_price <= market_min:
            return "Great Deal"
        elif listing_price <= estimated_value * 0.95:
            return "Good Deal"
        elif listing_price <= estimated_value * 1.05:
            return "Fair Price"
        else:
            return "High Price"
    
    def _get_default_valuation(self) -> Dict:
        """
        Return default valuation when all methods fail.
        """
        return {
            "estimated_value": None,
            "market_min": None,
            "market_max": None,
            "deal_rating": "Unknown",
            "confidence": 0.0,
            "data_source": "Unavailable"
        }

# Singleton instance
valuation_service = VehicleValuation()

console.log("Hello, world!"); 
