import { useEffect, useCallback } from 'react';

interface KeyboardNavigationOptions {
  enableArrows?: boolean;
  enableEscape?: boolean;
  enableEnter?: boolean;
  enableTab?: boolean;
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
  onEscape?: () => void;
  onEnter?: () => void;
  onTab?: (direction: 'forward' | 'backward') => void;
}

export const useKeyboardNavigation = (options: KeyboardNavigationOptions = {}) => {
  const {
    enableArrows = false,
    enableEscape = false,
    enableEnter = false,
    enableTab = false,
    onArrowUp,
    onArrowDown,
    onArrowLeft,
    onArrowRight,
    onEscape,
    onEnter,
    onTab,
  } = options;

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Don't interfere with form inputs
    if (
      event.target instanceof HTMLInputElement ||
      event.target instanceof HTMLTextAreaElement ||
      event.target instanceof HTMLSelectElement
    ) {
      return;
    }

    switch (event.key) {
      case 'ArrowUp':
        if (enableArrows && onArrowUp) {
          event.preventDefault();
          onArrowUp();
        }
        break;
      case 'ArrowDown':
        if (enableArrows && onArrowDown) {
          event.preventDefault();
          onArrowDown();
        }
        break;
      case 'ArrowLeft':
        if (enableArrows && onArrowLeft) {
          event.preventDefault();
          onArrowLeft();
        }
        break;
      case 'ArrowRight':
        if (enableArrows && onArrowRight) {
          event.preventDefault();
          onArrowRight();
        }
        break;
      case 'Escape':
        if (enableEscape && onEscape) {
          event.preventDefault();
          onEscape();
        }
        break;
      case 'Enter':
        if (enableEnter && onEnter) {
          event.preventDefault();
          onEnter();
        }
        break;
      case 'Tab':
        if (enableTab && onTab) {
          onTab(event.shiftKey ? 'backward' : 'forward');
        }
        break;
    }
  }, [enableArrows, enableEscape, enableEnter, enableTab, onArrowUp, onArrowDown, onArrowLeft, onArrowRight, onEscape, onEnter, onTab]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  return handleKeyDown;
};

export default useKeyboardNavigation;