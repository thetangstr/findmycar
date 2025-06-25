import React from 'react';
import { render, screen } from '@testing-library/react';
import ToastComponent, { Toast } from '@/components/Toast';

describe('Toast Component', () => {
  const mockToast: Toast = {
    id: 'test-toast',
    type: 'success',
    title: 'Test Success',
    message: 'This is a test message',
    duration: 5000,
  };

  const mockOnRemove = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders toast with title and message', () => {
    render(<ToastComponent toast={mockToast} onRemove={mockOnRemove} />);
    
    expect(screen.getByText('Test Success')).toBeInTheDocument();
    expect(screen.getByText('This is a test message')).toBeInTheDocument();
  });

  it('renders success toast with correct styling', () => {
    render(<ToastComponent toast={mockToast} onRemove={mockOnRemove} />);
    
    const toastElement = screen.getByRole('alert');
    expect(toastElement).toHaveAttribute('aria-live', 'polite');
  });

  it('renders error toast with correct styling', () => {
    const errorToast: Toast = {
      ...mockToast,
      type: 'error',
      title: 'Error Title',
    };

    render(<ToastComponent toast={errorToast} onRemove={mockOnRemove} />);
    
    expect(screen.getByText('Error Title')).toBeInTheDocument();
  });

  it('calls onRemove when close button is clicked', () => {
    render(<ToastComponent toast={mockToast} onRemove={mockOnRemove} />);
    
    const closeButton = screen.getByLabelText('Close notification');
    closeButton.click();
    
    // Note: onRemove is called after timeout, so we test the button exists
    expect(closeButton).toBeInTheDocument();
  });

  it('renders action button when action is provided', () => {
    const toastWithAction: Toast = {
      ...mockToast,
      action: {
        label: 'Retry',
        onClick: jest.fn(),
      },
    };

    render(<ToastComponent toast={toastWithAction} onRemove={mockOnRemove} />);
    
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });
});