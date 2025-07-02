import openai
from typing import Dict, Optional
from config import OPENAI_API_KEY

class CommunicationAssistant:
    """
    Generate communication templates and negotiation assistance for car buyers.
    """
    
    def __init__(self):
        self.openai_enabled = OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key"
        if self.openai_enabled:
            openai.api_key = OPENAI_API_KEY
    
    def generate_inquiry_message(self, vehicle_data: Dict, questions: list = None) -> str:
        """
        Generate an initial inquiry message template.
        """
        if self.openai_enabled:
            try:
                return self._generate_ai_inquiry(vehicle_data, questions)
            except Exception as e:
                print(f"AI inquiry generation failed: {e}")
        
        return self._generate_template_inquiry(vehicle_data, questions)
    
    def generate_offer_message(self, vehicle_data: Dict, offer_price: float, 
                             reasons: list = None) -> str:
        """
        Generate a negotiation/offer message template.
        """
        if self.openai_enabled:
            try:
                return self._generate_ai_offer(vehicle_data, offer_price, reasons)
            except Exception as e:
                print(f"AI offer generation failed: {e}")
        
        return self._generate_template_offer(vehicle_data, offer_price, reasons)
    
    def suggest_negotiation_points(self, vehicle_data: Dict) -> list:
        """
        Suggest negotiation points based on vehicle data.
        """
        points = []
        
        # Deal rating based points
        deal_rating = vehicle_data.get('deal_rating', '')
        if deal_rating == 'High Price':
            points.append("The asking price is above market value")
            if vehicle_data.get('estimated_value'):
                market_value = vehicle_data['estimated_value']
                asking_price = vehicle_data.get('price', 0)
                if asking_price > market_value:
                    savings = asking_price - market_value
                    points.append(f"Market value suggests ${savings:,.0f} savings potential")
        
        # Age and mileage points
        year = vehicle_data.get('year')
        if year:
            age = 2024 - year
            if age >= 5:
                points.append("Vehicle age may warrant lower price")
        
        mileage = vehicle_data.get('mileage')
        if mileage and year:
            expected_mileage = (2024 - year) * 12000
            if mileage > expected_mileage:
                excess = mileage - expected_mileage
                points.append(f"Higher than average mileage ({excess:,} miles over expected)")
        
        # Condition based
        condition = vehicle_data.get('condition', '').lower()
        if condition in ['fair', 'poor']:
            points.append("Vehicle condition may justify price reduction")
        
        return points
    
    def _generate_ai_inquiry(self, vehicle_data: Dict, questions: list = None) -> str:
        """
        Use AI to generate personalized inquiry message.
        """
        context = self._build_context(vehicle_data)
        questions_text = ""
        
        if questions:
            questions_text = f"\n\nSpecific questions:\n" + "\n".join([f"- {q}" for q in questions[:5]])
        
        prompt = f"""
        Generate a polite and professional initial inquiry message for a car buyer interested in this vehicle.
        Keep it concise but show genuine interest and knowledge.
        
        Vehicle: {context}
        {questions_text}
        
        Generate a message that:
        - Expresses genuine interest
        - Shows you've done research
        - Asks 2-3 key questions
        - Suggests next steps (viewing, more info)
        - Maintains professional tone
        
        Return just the message text, no subject line.
        """
        
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=300,
            temperature=0.3
        )
        
        return response.choices[0].text.strip()
    
    def _generate_ai_offer(self, vehicle_data: Dict, offer_price: float, 
                          reasons: list = None) -> str:
        """
        Use AI to generate negotiation/offer message.
        """
        context = self._build_context(vehicle_data)
        reasons_text = ""
        
        if reasons:
            reasons_text = f"\n\nNegotiation points:\n" + "\n".join([f"- {r}" for r in reasons])
        
        prompt = f"""
        Generate a respectful negotiation message for a car buyer making an offer.
        Be diplomatic but confident, backing up the offer with facts.
        
        Vehicle: {context}
        Offer Price: ${offer_price:,.0f}
        {reasons_text}
        
        Generate a message that:
        - States the offer clearly
        - Provides factual justification
        - Shows respect for the seller
        - Keeps the door open for counter-offers
        - Maintains professional tone
        
        Return just the message text.
        """
        
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=300,
            temperature=0.3
        )
        
        return response.choices[0].text.strip()
    
    def _generate_template_inquiry(self, vehicle_data: Dict, questions: list = None) -> str:
        """
        Generate template-based inquiry message.
        """
        vehicle_desc = self._get_vehicle_description(vehicle_data)
        
        message = f"Hello,\n\nI'm interested in your {vehicle_desc}"
        
        if vehicle_data.get('deal_rating') == 'Great Deal':
            message += " and noticed it appears to be priced competitively"
        
        message += ". I'd like to learn more about the vehicle."
        
        if questions and len(questions) > 0:
            message += " I have a few specific questions:\n\n"
            for i, question in enumerate(questions[:3], 1):
                message += f"{i}. {question}\n"
            message += "\n"
        
        message += "Would it be possible to schedule a viewing or get additional information? "
        message += "I'm a serious buyer and can move quickly if everything checks out.\n\n"
        message += "Thank you for your time.\n\nBest regards"
        
        return message
    
    def _generate_template_offer(self, vehicle_data: Dict, offer_price: float, 
                               reasons: list = None) -> str:
        """
        Generate template-based offer message.
        """
        vehicle_desc = self._get_vehicle_description(vehicle_data)
        asking_price = vehicle_data.get('price', 0)
        
        message = f"Hello,\n\nI'm very interested in your {vehicle_desc}. "
        message += f"After researching the vehicle and considering the market, "
        message += f"I'd like to make an offer of ${offer_price:,.0f}."
        
        if reasons and len(reasons) > 0:
            message += "\n\nMy offer is based on:\n"
            for reason in reasons[:3]:
                message += f"• {reason}\n"
        
        if asking_price > offer_price:
            difference = asking_price - offer_price
            percentage = (difference / asking_price) * 100
            if percentage < 15:  # Reasonable negotiation range
                message += f"\nI understand this is ${difference:,.0f} below your asking price, "
                message += "but I believe this reflects the current market conditions."
        
        message += "\n\nI'm a serious buyer with financing pre-approved and can close quickly. "
        message += "Please let me know if this works for you or if you'd like to discuss further.\n\n"
        message += "Thank you for considering my offer.\n\nBest regards"
        
        return message
    
    def _build_context(self, vehicle_data: Dict) -> str:
        """
        Build vehicle context for AI prompts.
        """
        parts = []
        
        if vehicle_data.get('year') and vehicle_data.get('make') and vehicle_data.get('model'):
            parts.append(f"{vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}")
        
        if vehicle_data.get('mileage'):
            parts.append(f"{vehicle_data['mileage']:,} miles")
        
        if vehicle_data.get('price'):
            parts.append(f"Listed at ${vehicle_data['price']:,.0f}")
        
        if vehicle_data.get('deal_rating'):
            parts.append(f"Deal rating: {vehicle_data['deal_rating']}")
        
        return ", ".join(parts)
    
    def _get_vehicle_description(self, vehicle_data: Dict) -> str:
        """
        Get a concise vehicle description.
        """
        if vehicle_data.get('year') and vehicle_data.get('make') and vehicle_data.get('model'):
            desc = f"{vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}"
            if vehicle_data.get('mileage'):
                desc += f" with {vehicle_data['mileage']:,} miles"
            return desc
        
        return vehicle_data.get('title', 'vehicle')

# Singleton instance
communication_assistant = CommunicationAssistant()