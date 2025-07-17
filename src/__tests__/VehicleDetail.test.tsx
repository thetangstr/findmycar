import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, expect, test, jest, beforeEach } from '@jest/globals';
import VehicleDetail from '../pages/vehicles/[id]';
import { useVehicles } from '../hooks/useVehicles';
import { useRecentlyViewed } from '../hooks/useRecentlyViewed';
import { useRouter } from 'next/router';

// Mock the hooks and modules
jest.mock('next/router', () => ({
  useRouter: jest.fn()
}));

jest.mock('../hooks/useVehicles', () => ({
  useVehicles: jest.fn()
}));

jest.mock('../hooks/useRecentlyViewed', () => ({
  useRecentlyViewed: jest.fn()
}));

jest.mock('../utils/auth', () => ({
  useAuth: () => ({ user: null })
}));

jest.mock('next/head', () => {
  return {
    __esModule: true,
    default: ({ children }: { children: React.ReactNode }) => <div data-testid="head">{children}</div>
  };
});

describe('VehicleDetail Page', () => {
  // Setup mock implementations
  const mockRouter = {
    query: { id: '1' },
    push: jest.fn()
  };
  
  const mockVehicle = {
    id: '1',
    make: 'Toyota',
    model: 'RAV4',
    year: 2023,
    price: 32999,
    mileage: 5621,
    exteriorColor: 'Silver',
    interiorColor: 'Black',
    fuelType: 'Hybrid',
    transmission: 'Automatic',
    engine: '2.5L 4-Cylinder',
    vin: 'JTMWRREV4PD123456',
    description: 'Like-new Toyota RAV4 Hybrid with excellent fuel economy and low mileage.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation'],
    images: ['/images/vehicles/rav4-1.jpg'],
    location: 'San Francisco, CA',
    dealer: 'Bay Area Toyota',
    listingDate: '2025-05-15',
    source: 'Dealer Website',
    url: '#'
  };
  
  const mockAddToRecentlyViewed = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (useRecentlyViewed as jest.Mock).mockReturnValue({
      addToRecentlyViewed: mockAddToRecentlyViewed
    });
  });
  
  test('shows loading state initially', () => {
    // Mock the loading state
    (useVehicles as jest.Mock).mockReturnValue({
      getVehicleById: jest.fn().mockResolvedValue(mockVehicle),
      vehicles: [],
      loading: true
    });
    
    render(<VehicleDetail />);
    
    expect(screen.getByText('Loading vehicle details...')).toBeInTheDocument();
  });
  
  test('shows vehicle not found when vehicle is null', async () => {
    // Mock a null vehicle return
    (useVehicles as jest.Mock).mockReturnValue({
      getVehicleById: jest.fn().mockResolvedValue(null),
      vehicles: [],
      loading: false
    });
    
    render(<VehicleDetail />);
    
    // Wait for the component to finish loading
    await waitFor(() => {
      expect(screen.getByText('Vehicle Not Found')).toBeInTheDocument();
    });
  });
  
  test('renders vehicle details correctly', async () => {
    // Mock a successful vehicle fetch
    (useVehicles as jest.Mock).mockReturnValue({
      getVehicleById: jest.fn().mockResolvedValue(mockVehicle),
      vehicles: [mockVehicle],
      loading: false
    });
    
    render(<VehicleDetail />);
    
    // Wait for the component to finish loading
    await waitFor(() => {
      // Check that the vehicle details are displayed
      expect(screen.getByText('2023 Toyota RAV4')).toBeInTheDocument();
      expect(screen.getByText('Hybrid')).toBeInTheDocument();
      expect(screen.getByText('Automatic')).toBeInTheDocument();
      expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
    });
    
    // Check that addToRecentlyViewed was called
    expect(mockAddToRecentlyViewed).toHaveBeenCalledWith('1');
  });
  
  test('handles null values gracefully', async () => {
    // Create a vehicle with some null values
    const vehicleWithNulls = {
      ...mockVehicle,
      price: null,
      mileage: null
    };
    
    // Mock the vehicle with nulls
    (useVehicles as jest.Mock).mockReturnValue({
      getVehicleById: jest.fn().mockResolvedValue(vehicleWithNulls),
      vehicles: [vehicleWithNulls],
      loading: false
    });
    
    render(<VehicleDetail />);
    
    // Wait for the component to finish loading and check that it doesn't crash
    await waitFor(() => {
      expect(screen.getByText('2023 Toyota RAV4')).toBeInTheDocument();
    });
    
    // The page should render without errors even with null values
    expect(screen.queryByText('TypeError')).not.toBeInTheDocument();
  });
});
