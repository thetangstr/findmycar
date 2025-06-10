# FindMyCar

A modern web application for aggregating car listings and implementing AI-powered search functionality.

## Features

### Core Features
1. **Listing Aggregation**
   - Browse car listings from multiple sources
   - Filter by make, model, year, price, mileage, and more
   - Sort listings by various criteria

2. **LLM-Powered Search**
   - Natural language search functionality
   - Intelligent matching based on user preferences
   - Example queries for easy exploration

3. **AI Buyer Insights** ✨ NEW
   - Gemini AI-powered buyer analysis for each vehicle
   - Comprehensive "Should I buy this car?" analysis
   - Detailed pros/cons, pricing analysis, and market positioning
   - Smart recommendation system with scoring (1-10)

4. **Trending Social Posts** ✨ NEW
   - AI-generated realistic social media content using Gemini
   - YouTube reviews, Reddit discussions, TikTok videos, and more
   - Platform filtering and relevance scoring
   - Popular hashtags and trending discussions
   - Realistic engagement metrics and author names

### Additional Features
- **Vehicle Comparison**
  - Compare up to 4 vehicles side by side
  - Floating comparison indicator
  - Detailed specification comparison

- **Saved Searches**
  - Save search criteria with custom names
  - Quickly access previous search parameters
  - Edit and manage saved searches

- **Search History**
  - Track recent searches
  - Easily reuse previous search criteria

- **Recently Viewed Vehicles**
  - Track browsing history
  - Quickly access previously viewed vehicles

- **Favorites System**
  - Save favorite vehicles
  - Dedicated favorites page

## Technology Stack

- **Frontend**: React with Next.js
- **Styling**: Tailwind CSS
- **State Management**: React Hooks
- **Data Persistence**: LocalStorage
- **AI Search**: Custom LLM implementation
- **AI Insights**: Google Gemini AI

## Project Structure

```
/src
  /components      # Reusable UI components
    AIInsightButton.tsx    # AI buyer analysis component
  /data            # Mock data and data utilities
  /hooks           # Custom React hooks
  /pages           # Next.js pages
  /services        # API services
    geminiService.ts       # Gemini AI integration
  /styles          # Global styles
  /types           # TypeScript type definitions
  /utils           # Utility functions
```

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Set up environment variables:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your API keys
   ```
4. Run the development server:
   ```
   npm run dev
   ```
5. Open [http://localhost:3000](http://localhost:3000) in your browser

## API Configuration

### Required API Keys

To enable all features, you'll need the following API keys:

1. **Google Gemini API** (for AI buyer insights)
   - Get your key from: https://makersuite.google.com/app/apikey
   - Add to `.env.local` as `NEXT_PUBLIC_GEMINI_API_KEY`

2. **OpenAI API** (for natural language search)
   - Get your key from: https://platform.openai.com/api-keys
   - Add to `.env.local` as `NEXT_PUBLIC_OPENAI_API_KEY`

3. **Note**: Social posts now use your existing Gemini API key to generate realistic content - no additional API setup needed!

### Environment Variables

Create a `.env.local` file in the root directory:

```bash
# Google Gemini API Key (for AI buyer insights)
NEXT_PUBLIC_GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API Key (for LLM search)
NEXT_PUBLIC_OPENAI_API_KEY=your_openai_api_key_here

# Note: Social posts use the Gemini API key above - no additional setup needed!
```

## Key Pages

- **Home** (`/`): Landing page with featured vehicles
- **Search** (`/search`): Advanced filtering and sorting
- **AI Search** (`/llm-search`): Natural language search interface
- **Vehicle Details** (`/vehicles/[id]`): Detailed vehicle information
- **Compare** (`/compare`): Side-by-side vehicle comparison
- **Favorites** (`/favorites`): Saved favorite vehicles
- **Recently Viewed** (`/recently-viewed`): Browsing history
- **Saved Searches** (`/saved-searches`): Saved search criteria

## AI Features

### AI Buyer Insights

Each vehicle card now includes an "AI Insights" button that provides:

- **Recommendation**: Buy/Consider/Avoid with reasoning
- **Score**: 1-10 rating based on multiple factors
- **Pros & Cons**: Detailed analysis of advantages and disadvantages
- **Price Analysis**: Market pricing evaluation
- **Market Position**: How the vehicle compares to similar options

The analysis considers factors like:
- Vehicle reliability and brand reputation
- Mileage appropriateness for the year
- Price competitiveness
- Potential maintenance costs
- Resale value
- Fuel efficiency
- Safety ratings

### Trending Social Posts

The vehicle detail page now includes a dedicated social posts section that shows:

- **AI-Generated Content**: Realistic social media posts powered by Gemini AI
- **Multiple Platforms**: YouTube, Reddit, TikTok, Instagram, and Twitter content
- **Platform Filtering**: Filter content by platform type
- **Relevance Scoring**: Posts ranked by relevance to the specific vehicle
- **Realistic Metrics**: Believable view counts, likes, and comments
- **Popular Hashtags**: Trending hashtags related to the vehicle
- **Diverse Content**: Reviews, comparisons, ownership experiences, test drives

The system uses AI to generate diverse, realistic social media content about each vehicle, providing buyers with a comprehensive view of what others might be saying about their potential purchase. No additional API keys required!
