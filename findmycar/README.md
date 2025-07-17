# CarGPT - AI-Powered Vehicle Discovery Platform

CarGPT is a comprehensive web application that simplifies the car buying experience by aggregating vehicle listings from multiple sources including eBay Motors, CarMax, and Bring a Trailer. It provides AI-powered insights, pricing analysis, and communication assistance.

## 🚀 Features Implemented

### ✅ Core Features (All Complete)
1. **Multi-Source Integration** - eBay Motors API, CarMax scraping, Bring a Trailer auctions
2. **Dual Search Interface** - Natural language queries + traditional filters
3. **Vehicle Valuation** - Market price analysis with deal ratings (Great Deal, Good Deal, Fair Price, High Price)
4. **AI-Powered Questions** - Contextual buyer questions generated for each vehicle
5. **Communication Assistance** - AI-generated inquiry and negotiation message templates
6. **Advanced Search** - Filter by make, model, year, price, location, and more
7. **Health Monitoring** - Real-time data source monitoring and testing framework
8. **Favorites System** - Save and manage favorite vehicles

### 🎯 Key Capabilities
- **Smart Search**: Type natural queries like "Honda Civic 2020 under $25k" or "truck for construction business"
- **Deal Analysis**: CarGurus-style price indicators showing market positioning
- **Buyer Intelligence**: AI suggests relevant questions based on vehicle specifics
- **Negotiation Support**: Generate professional inquiry and offer messages
- **Real-time Data**: Direct integration with eBay Motors Browse API

## 🛠 Technology Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite/PostgreSQL
- **Frontend**: Bootstrap 4 + Vanilla JavaScript
- **APIs**: eBay Browse API, OpenAI (optional), Vehicle valuation services
- **Web Scraping**: Selenium for CarMax and Bring a Trailer
- **Caching**: Redis for performance and rate limiting
- **Background Tasks**: Celery for async processing
- **Monitoring**: Health checks and data source monitoring
- **AI/ML**: Natural language processing for search queries and question generation

## 🔧 Setup & Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Update `.env` file with your API credentials:
   ```
   EBAY_CLIENT_ID=your-ebay-client-id
   EBAY_CLIENT_SECRET=your-ebay-client-secret
   OPENAI_API_KEY=your-openai-key  # Optional
   ```

3. **Run the Application**:
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the App**:
   Open http://localhost:8000 in your browser

## 🎮 How to Use

1. **Search for Vehicles**: Use natural language or specific filters
2. **Analyze Deals**: View price comparisons and deal ratings
3. **Get Smart Questions**: AI suggests what to ask sellers
4. **Generate Messages**: Create professional inquiry or offer templates
5. **Contact Sellers**: Copy generated messages to reach out on eBay

## 📊 Features Overview

### Search Interface
- Natural language: "red convertible sports cars under $40k"
- Traditional filters: make, model, year, price ranges
- Advanced filtering by body style, transmission, fuel type

### Price Analysis
- Market value estimation using industry algorithms
- Deal rating badges with color-coded indicators
- Price comparison bars showing market positioning

### AI Features
- Contextual questions based on vehicle age, mileage, location
- Communication templates for inquiries and offers
- Negotiation point suggestions

### User Interface
- Responsive design for desktop and mobile
- Card-based vehicle listings with rich information
- Collapsible sections for questions and details
- Modal dialogs for message generation

## 🔮 Future Enhancements

- Vehicle history report integration (Carfax, AutoCheck)
- Saved searches and alerts
- Advanced negotiation coaching
- Financing and insurance integrations
- Mobile app versions
- Additional data sources (Cars.com, Autotrader, etc.)
- Enhanced AI features for market predictions
- Advanced analytics and reporting

## 📁 Project Structure

```
findmycar/
├── main.py              # FastAPI application
├── database.py          # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── ebay_client.py       # eBay Browse API integration
├── carmax_client.py     # CarMax web scraping
├── bat_client.py        # Bring a Trailer scraping
├── cache.py             # Redis caching and rate limiting
├── tasks.py             # Celery background tasks
├── health_monitor.py    # Data source health monitoring
├── test_framework.py    # Comprehensive testing framework
├── nlp_search.py        # Natural language processing
├── valuation.py         # Vehicle pricing analysis
├── ai_questions.py      # AI question generation
├── communication.py     # Message templates
├── ingestion.py         # Data processing
├── crud.py             # Database operations
├── templates/          # HTML templates
└── requirements.txt    # Dependencies
```

## 🏆 Implementation Highlights

This implementation successfully delivers all core features and has been significantly enhanced:

- **Multi-Source Aggregation**: Integrated eBay Motors, CarMax, and Bring a Trailer
- **Intelligent Search**: Combined rule-based and AI-powered natural language processing
- **Market Intelligence**: Implemented vehicle valuation with deal rating system
- **User Empowerment**: AI-generated questions help buyers ask the right questions
- **Communication Tools**: Professional message templates for seller outreach
- **Production Ready**: Health monitoring, caching, background tasks, and comprehensive testing
- **Robust Architecture**: Scalable design with proper error handling and monitoring

The platform provides a solid foundation for future enhancements and demonstrates a complete end-to-end car buying assistance solution with enterprise-grade reliability.
