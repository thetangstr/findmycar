import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AIInsightButton from '../components/AIInsightButton';
import { Vehicle } from '../types';
import * as geminiService from '../services/geminiService';

// Mock the Gemini service
jest.mock('../services/geminiService');
const mockGenerateBuyerAnalysis = geminiService.generateBuyerAnalysis as jest.MockedFunction<typeof geminiService.generateBuyerAnalysis>;

const mockVehicle: Vehicle = {
  id: '1',
  make: 'Toyota',
  model: 'Camry',
  year: 2020,
  price: 25000,
  mileage: 30000,
  exteriorColor: 'Silver',
  interiorColor: 'Black',
  fuelType: 'Gasoline',
  transmission: 'Automatic',
  engine: '2.5L 4-Cylinder',
  vin: 'TEST123456789',
  description: 'Well-maintained Toyota Camry with low mileage',
  features: ['Backup Camera', 'Bluetooth', 'Cruise Control'],
  images: ['https://example.com/image1.jpg'],
  location: 'Los Angeles, CA',
  dealer: 'Test Dealer',
  listingDate: '2024-01-01',
  source: 'test',
  url: 'https://example.com/vehicle/1'
};

const mockAnalysis = {
  recommendation: 'buy' as const,
  score: 8,
  pros: ['Reliable brand', 'Low mileage', 'Good fuel economy'],
  cons: ['Higher price point', 'Common model'],
  summary: 'This Toyota Camry appears to be a solid choice for buyers.',
  priceAnalysis: 'Price is competitive for the year and mileage.',
  marketPosition: 'Strong position in the mid-size sedan market.'
};

describe('AIInsightButton', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the AI Insights button', () => {
    render(<AIInsightButton vehicle={mockVehicle} />);
    expect(screen.getByText('AI Insights')).toBeInTheDocument();
  });

  it('shows loading state when analyzing', async () => {
    // Mock a delayed response
    mockGenerateBuyerAnalysis.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve(mockAnalysis), 100))
    );

    render(<AIInsightButton vehicle={mockVehicle} />);
    
    const button = screen.getByText('AI Insights');
    fireEvent.click(button);

    expect(screen.getByText('Analyzing...')).toBeInTheDocument();
    expect(button).toBeDisabled();

    await waitFor(() => expect(screen.queryByText('Analyzing...')).not.toBeInTheDocument());
  });

  it('displays analysis modal when analysis completes', async () => {
    mockGenerateBuyerAnalysis.mockResolvedValue(mockAnalysis);

    render(<AIInsightButton vehicle={mockVehicle} />);
    
    const button = screen.getByText('AI Insights');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('🤖 AI Buyer\'s Analysis')).toBeInTheDocument();
      expect(screen.getByText('BUY')).toBeInTheDocument();
      expect(screen.getByText('8/10')).toBeInTheDocument();
      expect(screen.getByText('This Toyota Camry appears to be a solid choice for buyers.')).toBeInTheDocument();
    });
  });

  it('closes modal when close button is clicked', async () => {
    mockGenerateBuyerAnalysis.mockResolvedValue(mockAnalysis);

    render(<AIInsightButton vehicle={mockVehicle} />);
    
    const button = screen.getByText('AI Insights');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('🤖 AI Buyer\'s Analysis')).toBeInTheDocument();
    });

    const closeButton = screen.getByLabelText(/close/i) || screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);

    await waitFor(() => {
      expect(screen.queryByText('🤖 AI Buyer\'s Analysis')).not.toBeInTheDocument();
    });
  });

  it('displays pros and cons correctly', async () => {
    mockGenerateBuyerAnalysis.mockResolvedValue(mockAnalysis);

    render(<AIInsightButton vehicle={mockVehicle} />);
    
    const button = screen.getByText('AI Insights');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Reliable brand')).toBeInTheDocument();
      expect(screen.getByText('Low mileage')).toBeInTheDocument();
      expect(screen.getByText('Good fuel economy')).toBeInTheDocument();
      expect(screen.getByText('Higher price point')).toBeInTheDocument();
      expect(screen.getByText('Common model')).toBeInTheDocument();
    });
  });

  it('handles custom className prop', () => {
    render(<AIInsightButton vehicle={mockVehicle} className="custom-class" />);
    const button = screen.getByText('AI Insights');
    expect(button).toHaveClass('custom-class');
  });
}); 