import { useState, useCallback } from 'react';
import { Toast, ToastType } from '@/components/Toast';

let toastIdCounter = 0;

export const useToast = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((
    type: ToastType,
    title: string,
    message?: string,
    options?: {
      duration?: number;
      action?: {
        label: string;
        onClick: () => void;
      };
    }
  ) => {
    const id = `toast-${++toastIdCounter}`;
    const newToast: Toast = {
      id,
      type,
      title,
      message,
      duration: options?.duration,
      action: options?.action,
    };

    setToasts(prev => [...prev, newToast]);
    return id;
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const removeAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  // Convenience methods
  const success = useCallback((title: string, message?: string, options?: Parameters<typeof addToast>[3]) => 
    addToast('success', title, message, options), [addToast]);

  const error = useCallback((title: string, message?: string, options?: Parameters<typeof addToast>[3]) => 
    addToast('error', title, message, options), [addToast]);

  const warning = useCallback((title: string, message?: string, options?: Parameters<typeof addToast>[3]) => 
    addToast('warning', title, message, options), [addToast]);

  const info = useCallback((title: string, message?: string, options?: Parameters<typeof addToast>[3]) => 
    addToast('info', title, message, options), [addToast]);

  return {
    toasts,
    addToast,
    removeToast,
    removeAllToasts,
    success,
    error,
    warning,
    info,
  };
};

export default useToast;