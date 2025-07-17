import { useState, useEffect, useCallback } from 'react';
import { SearchFilters } from '@/types';
import { useAuth } from '@/utils/auth';

export interface Alert {
  id: string;
  name: string;
  filters: SearchFilters;
  frequency: 'daily' | 'weekly' | 'instant';
  createdAt: string;
  lastSentAt?: string;
}

export const useAlerts = () => {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load alerts from localStorage on initial render
  useEffect(() => {
    const loadAlerts = () => {
      setLoading(true);
      try {
        const storedAlerts = localStorage.getItem('vehicle_alerts');
        if (storedAlerts) {
          setAlerts(JSON.parse(storedAlerts));
        }
      } catch (err) {
        console.error('Failed to load alerts:', err);
        setError('Failed to load your alerts');
      } finally {
        setLoading(false);
      }
    };

    loadAlerts();
  }, []);

  // Save alerts to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('vehicle_alerts', JSON.stringify(alerts));
  }, [alerts]);

  // Create a new alert
  const createAlert = useCallback((name: string, filters: SearchFilters, frequency: 'daily' | 'weekly' | 'instant') => {
    const newAlert: Alert = {
      id: Date.now().toString(),
      name,
      filters,
      frequency,
      createdAt: new Date().toISOString()
    };

    setAlerts(prev => [...prev, newAlert]);
    return newAlert;
  }, []);

  // Update an existing alert
  const updateAlert = useCallback((id: string, updates: Partial<Alert>) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === id ? { ...alert, ...updates } : alert
      )
    );
  }, []);

  // Delete an alert
  const deleteAlert = useCallback((id: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  }, []);

  // Test an alert (simulate sending)
  const testAlert = useCallback(async (id: string): Promise<boolean> => {
    try {
      // In a real app, this would make an API call to send a test alert
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update the lastSentAt timestamp
      setAlerts(prev => 
        prev.map(alert => 
          alert.id === id 
            ? { ...alert, lastSentAt: new Date().toISOString() } 
            : alert
        )
      );
      
      return true;
    } catch (err) {
      console.error('Failed to test alert:', err);
      return false;
    }
  }, []);

  return {
    alerts,
    loading,
    error,
    createAlert,
    updateAlert,
    deleteAlert,
    testAlert
  };
};

export default useAlerts;
