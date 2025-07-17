/**
 * Utility to detect and remove problematic elements with rendering issues
 * This helps prevent garbled characters or encoding issues in the UI
 */

/**
 * Runs DOM cleanup to remove elements with rendering issues
 * This should be called on the client side only
 */
export const cleanupGarbledElements = (): void => {
  if (typeof window === 'undefined') return;
  
  try {
    console.log('Running cleanup for problematic rendering elements');
    
    // Look for elements with unusual or suspicious text content
    const allElements = document.querySelectorAll('div, span, p, a, h1, h2, h3, h4, h5, h6');
    
    allElements.forEach(element => {
      // Skip elements that are part of our core UI components
      if (element.closest('.Hero') || element.closest('.Footer') || 
          element.closest('.WhyChooseUs') || element.closest('.HowItWorks') ||
          element.closest('.PartnerSection')) {
        return;
      }
      
      // TypeScript type casting for DOM element properties
      const htmlElement = element as HTMLElement;
      const text = htmlElement.innerText || '';
      
      // Look for strings that match the garbled text pattern
      if (
        text.includes('FireFoxy') || 
        text.includes('Patriot') ||
        /[\uFFFD\uD800-\uDBFF]/.test(text) || // Unicode replacement character or surrogate pairs
        // Check for elements with a mix of Latin letters and unusual Unicode characters
        (/[a-zA-Z]/.test(text) && /[\u2000-\u206F\u2190-\u21FF\u2600-\u26FF]/.test(text))
      ) {
        console.log('Found element with rendering issues:', text);
        
        // Hide the problematic element (with proper type casting)
        htmlElement.style.display = 'none';
      }
    });
  } catch (error) {
    console.error('Error in garbled text cleanup:', error);
    // Fail gracefully - don't break the app if cleanup fails
  }
};

export default cleanupGarbledElements;
