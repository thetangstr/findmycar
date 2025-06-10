import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, expect, test, jest, beforeEach } from '@jest/globals';
import NaturalLanguageSearch from '../components/NaturalLanguageSearch';

describe('NaturalLanguageSearch Component', () => {
  const mockOnSearch = jest.fn();
  
  beforeEach(() => {
    mockOnSearch.mockClear();
  });
  
  test('renders correctly with all elements', () => {
    render(<NaturalLanguageSearch onSearch={mockOnSearch} />);
    
    // Check that the component renders with the correct elements
    expect(screen.getByText('Natural Language Search')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('What kind of vehicle are you looking for?')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Search' })).toBeInTheDocument();
    expect(screen.getByText('Try these examples:')).toBeInTheDocument();
  });
  
  test('search button is disabled when input is empty', () => {
    render(<NaturalLanguageSearch onSearch={mockOnSearch} />);
    
    const searchButton = screen.getByRole('button', { name: 'Search' });
    const input = screen.getByPlaceholderText('What kind of vehicle are you looking for?');
    
    // Button should be disabled initially
    expect(searchButton).toBeDisabled();
    
    // Button should be enabled when input has text
    fireEvent.change(input, { target: { value: 'SUV under 40k' } });
    expect(searchButton).not.toBeDisabled();
    
    // Button should be disabled again when input is cleared
    fireEvent.change(input, { target: { value: '' } });
    expect(searchButton).toBeDisabled();
  });
  
  test('calls onSearch with correct filters when search button is clicked', async () => {
    render(<NaturalLanguageSearch onSearch={mockOnSearch} />);
    
    const searchButton = screen.getByRole('button', { name: 'Search' });
    const input = screen.getByPlaceholderText('What kind of vehicle are you looking for?');
    
    // Enter a search query
    fireEvent.change(input, { target: { value: 'SUV under 40k' } });
    
    // Click the search button
    fireEvent.click(searchButton);
    
    // Check that onSearch was called with the correct filters
    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledTimes(1);
      
      // The exact filters will depend on the implementation of the parseQuery function
      // but we can check that bodyType and priceMax are set correctly
      const filters = mockOnSearch.mock.calls[0][0];
      expect(filters).toHaveProperty('bodyType', 'SUV');
      expect(filters).toHaveProperty('priceMax', 40000);
    });
  });
  
  test('calls onSearch when Enter key is pressed', async () => {
    render(<NaturalLanguageSearch onSearch={mockOnSearch} />);
    
    const input = screen.getByPlaceholderText('What kind of vehicle are you looking for?');
    
    // Enter a search query
    fireEvent.change(input, { target: { value: 'Hybrid sedan' } });
    
    // Press Enter
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    
    // Check that onSearch was called with the correct filters
    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledTimes(1);
      
      const filters = mockOnSearch.mock.calls[0][0];
      expect(filters).toHaveProperty('bodyType', 'Sedan');
      expect(filters).toHaveProperty('fuelType', 'Hybrid');
    });
  });
  
  test('parses complex queries correctly', async () => {
    render(<NaturalLanguageSearch onSearch={mockOnSearch} />);
    
    const input = screen.getByPlaceholderText('What kind of vehicle are you looking for?');
    
    // Enter a complex search query
    fireEvent.change(input, { target: { value: '2022 Toyota RAV4 Hybrid with leather seats and sunroof under 35k' } });
    
    // Click the search button
    fireEvent.click(screen.getByRole('button', { name: 'Search' }));
    
    // Check that onSearch was called with the correct filters
    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledTimes(1);
      
      const filters = mockOnSearch.mock.calls[0][0];
      expect(filters).toHaveProperty('make', 'Toyota');
      expect(filters).toHaveProperty('model', 'RAV4');
      expect(filters).toHaveProperty('yearMin', 2022);
      expect(filters).toHaveProperty('fuelType', 'Hybrid');
      expect(filters).toHaveProperty('priceMax', 35000);
      expect(filters.features).toContain('Leather Seats');
      expect(filters.features).toContain('Sunroof');
    });
  });
});
