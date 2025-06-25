# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FindMyCar is a Next.js web application that implements the AutoNavigator vision - a unified car search and acquisition platform. The app aggregates vehicle listings from multiple sources (Bring a Trailer, mock dealership data) and provides AI-powered search, vehicle analysis, and buyer insights.

## Core Architecture

### Technology Stack
- **Frontend**: Next.js 14 with React 18, TypeScript, Tailwind CSS  
- **State Management**: React hooks, Zustand for complex state
- **AI Integration**: Google Gemini AI for buyer insights, OpenAI for natural language search
- **Data Sources**: Bring a Trailer API, mock vehicle data, featured vehicles service
- **Styling**: Tailwind CSS with custom components
- **Testing**: Jest + React Testing Library, Playwright for E2E

### Key Services Architecture
- `vehicleApi.ts` - Main vehicle data aggregation service that combines multiple sources
- `batVehicleApi.ts` - Bring a Trailer specific API integration  
- `geminiService.ts` - AI-powered buyer analysis and vehicle insights
- `intelligentSearchService.ts` - Natural language search processing
- `featuredVehiclesService.ts` - Curated vehicle listings management

### Data Flow
1. Vehicle data is fetched from multiple sources (BAT API, mock data, featured vehicles)
2. Search queries are processed through intelligent search service for NLP
3. Vehicle details are enhanced with AI-generated buyer insights via Gemini
4. Social media content is generated dynamically for each vehicle
5. User interactions (favorites, comparison, search history) are stored in localStorage

## Development Commands

### Essential Commands
```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server  
npm start

# Linting
npm run lint

# Testing
npm run test           # Unit tests
npm run test:watch     # Watch mode
npm run test:e2e       # Playwright E2E tests
npm run test:e2e:ui    # Playwright UI mode
```

### Environment Setup
Create `.env.local` with:
```bash
NEXT_PUBLIC_GEMINI_API_KEY=your_gemini_api_key
NEXT_PUBLIC_OPENAI_API_KEY=your_openai_api_key
```

## Key Components & Features

### Search Architecture
- **Dual Search Interface**: Traditional filters + natural language prompts
- **Intelligent Search**: Uses OpenAI to parse user intent from natural language
- **Multi-Source Aggregation**: Combines BAT listings, featured vehicles, and mock data
- **Real-time Filtering**: Client-side filtering with comprehensive search parameters

### AI-Powered Features
- **Buyer Analysis**: Gemini AI generates detailed purchase recommendations with scoring (1-10)
- **Vehicle Insights**: Comprehensive pros/cons analysis, market positioning, price analysis
- **Social Media Generation**: AI-generated realistic social posts about vehicles
- **Collector Focus**: Special analysis for classic/collectible vehicles (Porsche 964, NSX, etc.)

### Core Pages
- `/` - Home page with featured vehicles and hero section
- `/search` - Advanced search with filters and sorting
- `/llm-search` - Natural language search interface  
- `/vehicles/[id]` - Vehicle detail page with AI insights and social posts
- `/compare` - Side-by-side vehicle comparison (up to 4 vehicles)
- `/favorites` - Saved favorite vehicles
- `/saved-searches` - Saved search criteria management

### State Management Patterns
- **Local Storage**: Favorites, comparison items, search history, recently viewed
- **Custom Hooks**: `useFavorites`, `useComparison`, `useSearchHistory`, `useRecentlyViewed`
- **Search State**: Managed through URL parameters and local component state

## Important Implementation Details

### Vehicle Data Structure
The `Vehicle` interface includes enhanced fields for collector analysis:
- `appreciationData` - Market appreciation tracking
- `vehicleHistory` - History reports integration ready
- `sellerNotes` - Additional seller information
- Image loading state management for better UX

### AI Integration Patterns
- **Fallback Strategy**: When Gemini API unavailable, use hardcoded analysis for known vehicles
- **Collector-Focused**: Special handling for classics (Porsche 964, NSX, Corvette Z06)
- **Context-Aware**: Analysis considers vehicle age, mileage, market position
- **JSON Response Parsing**: Robust parsing of AI-generated structured responses

### Search Implementation
- **Multi-Modal**: Supports both structured filters and natural language
- **Source Filtering**: Can filter by data source (BAT, featured, etc.)
- **Intelligent Matching**: NLP processing for queries like "red convertible sports cars under $30k"
- **Pagination Ready**: Architecture supports pagination (currently client-side)

### Testing Strategy
- **Unit Tests**: Key components like AI insights, search functionality, vehicle API
- **E2E Tests**: Critical user flows with Playwright
- **Mock Data**: Comprehensive mock vehicle data for development and testing

## PRD Alignment

This codebase implements the core AutoNavigator features from the PRD:

1. **Aggregated Search** - Multi-source vehicle listings ✓
2. **Dual Search Interface** - Natural language + traditional filters ✓  
3. **AI-Generated Insights** - Buyer analysis and recommendations ✓
4. **Vehicle Information** - Enhanced with market analysis and social content ✓
5. **Communication Tools** - Foundation for negotiation features (planned)

The architecture is designed to easily integrate additional data sources, expand AI capabilities, and add the negotiation features outlined in the PRD's future scope.

## Code Conventions

- Use TypeScript for all new code
- Follow Next.js app router patterns
- Tailwind CSS for styling with custom component patterns
- Error boundaries and graceful fallbacks for AI services
- Consistent prop interfaces and component composition
- localStorage utilities in hooks for client-side persistence