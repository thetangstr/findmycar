import { useRef, useCallback, useEffect } from 'react';

interface FocusManagementOptions {
  restoreFocus?: boolean;
  trapFocus?: boolean;
  initialFocus?: boolean;
}

export const useFocusManagement = (isActive: boolean, options: FocusManagementOptions = {}) => {
  const { restoreFocus = true, trapFocus = false, initialFocus = true } = options;
  const containerRef = useRef<HTMLElement>(null);
  const previousActiveElement = useRef<Element | null>(null);

  // Store the previously focused element when becoming active
  useEffect(() => {
    if (isActive) {
      previousActiveElement.current = document.activeElement;
      
      if (initialFocus && containerRef.current) {
        // Focus the container or the first focusable element within it
        const firstFocusable = getFocusableElements(containerRef.current)[0];
        if (firstFocusable) {
          firstFocusable.focus();
        } else {
          containerRef.current.focus();
        }
      }
    } else if (restoreFocus && previousActiveElement.current) {
      // Restore focus when becoming inactive
      (previousActiveElement.current as HTMLElement).focus();
      previousActiveElement.current = null;
    }
  }, [isActive, restoreFocus, initialFocus]);

  // Handle focus trapping
  useEffect(() => {
    if (!isActive || !trapFocus || !containerRef.current) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return;

      const focusableElements = getFocusableElements(containerRef.current!);
      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (event.shiftKey) {
        // Shift + Tab (backwards)
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab (forwards)
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isActive, trapFocus]);

  const focusFirst = useCallback(() => {
    if (containerRef.current) {
      const firstFocusable = getFocusableElements(containerRef.current)[0];
      if (firstFocusable) {
        firstFocusable.focus();
      }
    }
  }, []);

  const focusLast = useCallback(() => {
    if (containerRef.current) {
      const focusableElements = getFocusableElements(containerRef.current);
      const lastFocusable = focusableElements[focusableElements.length - 1];
      if (lastFocusable) {
        lastFocusable.focus();
      }
    }
  }, []);

  return {
    containerRef,
    focusFirst,
    focusLast,
  };
};

// Helper function to get all focusable elements within a container
function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const focusableSelectors = [
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    'a[href]',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable="true"]',
  ].join(', ');

  return Array.from(container.querySelectorAll(focusableSelectors)) as HTMLElement[];
}

export default useFocusManagement;