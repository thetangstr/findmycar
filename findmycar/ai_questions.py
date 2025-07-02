import openai
import json
from typing import List, Dict, Optional
from config import OPENAI_API_KEY

class AIQuestionGenerator:
    """
    Generate contextual questions for car buyers based on vehicle details.
    """
    
    def __init__(self):
        self.openai_enabled = OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key"
        if self.openai_enabled:
            openai.api_key = OPENAI_API_KEY
    
    def generate_buyer_questions(self, vehicle_data: Dict) -> List[str]:
        """
        Generate contextual questions for a specific vehicle.
        
        Args:
            vehicle_data: Dictionary containing vehicle information
            
        Returns:
            List of relevant questions for the buyer to ask
        """
        
        # Try AI generation first if available
        if self.openai_enabled:
            try:
                ai_questions = self._generate_ai_questions(vehicle_data)
                if ai_questions:
                    return ai_questions
            except Exception as e:
                print(f"AI question generation failed: {e}")
        
        # Fallback to rule-based questions
        return self._generate_rule_based_questions(vehicle_data)
    
    def _generate_ai_questions(self, vehicle_data: Dict) -> Optional[List[str]]:
        """
        Use OpenAI to generate contextual questions.
        """
        try:
            # Build context from vehicle data
            context = self._build_vehicle_context(vehicle_data)
            
            prompt = f"""
            As an expert car buying advisor, generate 5-8 important questions a buyer should ask about this specific vehicle. 
            Focus on potential concerns, maintenance needs, and verification points based on the vehicle's details.
            
            Vehicle Details:
            {context}
            
            Generate questions that are:
            - Specific to this vehicle's characteristics
            - Practical and actionable
            - Help identify potential issues or concerns
            - Appropriate for the vehicle's age, mileage, and type
            
            Return as a JSON array of strings. Example format: ["Question 1?", "Question 2?"]
            """
            
            response = openai.Completion.create(
                engine="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=400,
                temperature=0.3
            )
            
            # Parse the JSON response
            response_text = response.choices[0].text.strip()
            questions = json.loads(response_text)
            
            # Validate and clean questions
            if isinstance(questions, list) and len(questions) > 0:
                return [q for q in questions if isinstance(q, str) and len(q.strip()) > 10]
            
        except Exception as e:
            print(f"OpenAI question generation error: {e}")
            
        return None
    
    def _generate_rule_based_questions(self, vehicle_data: Dict) -> List[str]:
        """
        Generate questions using rule-based logic.
        """
        questions = []
        
        # Basic questions for all vehicles
        questions.extend([
            "Are you the original owner of this vehicle?",
            "Do you have maintenance records available?",
            "Has the vehicle ever been in any accidents?",
            "Are there any known mechanical issues?"
        ])
        
        # Age-based questions
        year = vehicle_data.get('year')
        if year:
            current_year = 2024
            age = current_year - year
            
            if age >= 10:
                questions.extend([
                    "What major maintenance has been performed recently?",
                    "Have any major components been replaced (engine, transmission, etc.)?",
                    "Are there any rust or corrosion issues?"
                ])
            elif age >= 5:
                questions.extend([
                    "Is the vehicle still under any warranty?",
                    "What routine maintenance has been kept up with?"
                ])
        
        # Mileage-based questions  
        mileage = vehicle_data.get('mileage')
        if mileage:
            if mileage > 100000:
                questions.extend([
                    "Has the timing belt been replaced (if applicable)?",
                    "What major services have been performed for high mileage?",
                    "Are there any signs of excessive wear?"
                ])
            elif mileage > 50000:
                questions.append("Has the vehicle had any major services recently?")
            elif mileage < 20000:
                questions.append("Why is the mileage so low for the year?")
        
        # Make/model specific questions
        make = vehicle_data.get('make', '').lower()
        model = vehicle_data.get('model', '').lower()
        
        if make in ['bmw', 'mercedes', 'audi']:
            questions.extend([
                "Are all electronic systems functioning properly?",
                "Has the vehicle been serviced at authorized dealers?",
                "Are there any warning lights on the dashboard?"
            ])
        
        if make == 'subaru':
            questions.append("Has the head gasket been inspected or replaced?")
        
        if make == 'honda' and 'accord' in model:
            questions.append("Has the transmission been serviced regularly?")
        
        if make == 'toyota' and 'prius' in model:
            questions.extend([
                "How is the hybrid battery performing?",
                "When was the last hybrid system inspection?"
            ])
        
        # Vehicle type specific questions
        body_style = (vehicle_data.get('body_style') or '').lower()
        title = (vehicle_data.get('title') or '').lower()
        
        if 'truck' in body_style or 'pickup' in title:
            questions.extend([
                "What was this truck primarily used for?",
                "Has it been used for towing? If so, how frequently?",
                "Is the bed liner original or aftermarket?"
            ])
        
        if 'convertible' in body_style or 'convertible' in title:
            questions.extend([
                "How often was the top operated?",
                "Are there any issues with the convertible mechanism?",
                "Has the soft top been replaced or repaired?"
            ])
        
        if 'suv' in body_style:
            questions.extend([
                "Has this been used for off-roading?",
                "Are all-wheel drive systems functioning properly?"
            ])
        
        # Transmission specific
        transmission = (vehicle_data.get('transmission') or '').lower()
        if 'manual' in transmission:
            questions.extend([
                "How does the clutch feel? Any slipping?",
                "When was the clutch last replaced?",
                "Are all gears shifting smoothly?"
            ])
        elif 'automatic' in transmission:
            questions.append("Does the transmission shift smoothly without hesitation?")
        
        # Location-based questions
        location = (vehicle_data.get('location') or '').lower()
        if any(state in location for state in ['ny', 'new york', 'maine', 'vermont', 'new hampshire', 'massachusetts', 'connecticut']):
            questions.append("Has the vehicle been regularly treated for salt/winter road conditions?")
        
        if any(state in location for state in ['florida', 'arizona', 'nevada', 'california']):
            questions.append("How has the vehicle been protected from sun/heat damage?")
        
        # Price-based questions
        deal_rating = vehicle_data.get('deal_rating', '')
        if deal_rating == 'High Price':
            questions.append("Is there room for negotiation on the price?")
        elif deal_rating == 'Great Deal':
            questions.append("Is there any specific reason the price is lower than market value?")
        
        # Remove duplicates and return
        return list(dict.fromkeys(questions))  # Preserves order while removing duplicates
    
    def _build_vehicle_context(self, vehicle_data: Dict) -> str:
        """
        Build a context string from vehicle data for AI processing.
        """
        context_parts = []
        
        # Basic info
        if vehicle_data.get('year') and vehicle_data.get('make') and vehicle_data.get('model'):
            context_parts.append(f"Vehicle: {vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}")
        
        if vehicle_data.get('mileage'):
            context_parts.append(f"Mileage: {vehicle_data['mileage']:,} miles")
        
        if vehicle_data.get('condition'):
            context_parts.append(f"Condition: {vehicle_data['condition']}")
        
        if vehicle_data.get('transmission'):
            context_parts.append(f"Transmission: {vehicle_data['transmission']}")
        
        if vehicle_data.get('fuel_type'):
            context_parts.append(f"Fuel Type: {vehicle_data['fuel_type']}")
        
        if vehicle_data.get('location'):
            context_parts.append(f"Location: {vehicle_data['location']}")
        
        # Price analysis
        if vehicle_data.get('price') and vehicle_data.get('estimated_value'):
            context_parts.append(f"Listed Price: ${vehicle_data['price']:,.0f}")
            context_parts.append(f"Estimated Value: ${vehicle_data['estimated_value']:,.0f}")
        
        if vehicle_data.get('deal_rating'):
            context_parts.append(f"Deal Rating: {vehicle_data['deal_rating']}")
        
        # Age calculation
        if vehicle_data.get('year'):
            age = 2024 - vehicle_data['year']
            context_parts.append(f"Age: {age} years old")
        
        return "\n".join(context_parts)

# Singleton instance
question_generator = AIQuestionGenerator()