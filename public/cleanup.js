// Immediate self-executing function to clean up unwanted elements as early as possible
(function() {
  function cleanUpPage() {
    // Target specific text patterns
    const badTextPatterns = ['FireFoxy', 'Patriot', '&amp;', ' More!'];
    
    // Function to check if an element or its children contain bad text
    function containsBadText(element) {
      if (!element) return false;
      
      // Check the element's text content
      const text = element.textContent || '';
      for (const pattern of badTextPatterns) {
        if (text.includes(pattern)) return true;
      }
      
      return false;
    }
    
    // Function to remove entire sections that might be causing problems
    function removeProblematicSections() {
      // Remove any suspicious elements at the bottom of the page
      const body = document.body;
      if (!body) return;
      
      // 1. Find and remove any undesired elements at the bottom
      const allDivs = document.querySelectorAll('body > div');
      for (let i = allDivs.length - 1; i >= 0; i--) {
        const div = allDivs[i];
        
        // Skip the main app div
        if (div.className && div.className.includes('min-h-screen')) {
          continue;
        }
        
        // If this is a non-core div at the bottom, remove it
        if (!div.className || !div.className.includes('app') || containsBadText(div)) {
          if (div.parentNode) {
            div.parentNode.removeChild(div);
          }
        }
      }
      
      // 2. Find and remove any elements with bad class names 
      const suspiciousClasses = ['fire', 'foxy', 'patr', 'bann', 'ads'];
      
      for (const className of suspiciousClasses) {
        const elements = document.querySelectorAll(`[class*="${className}"]`);
        elements.forEach(el => {
          if (el.parentNode) {
            el.parentNode.removeChild(el);
          }
        });
      }
      
      // 3. Look specifically for any banner-like elements at the bottom of the page
      const footerEl = document.querySelector('footer');
      if (footerEl) {
        // Remove any elements that appear after the footer
        let nextSibling = footerEl.nextSibling;
        while (nextSibling) {
          const toRemove = nextSibling;
          nextSibling = nextSibling.nextSibling;
          if (toRemove.parentNode) {
            toRemove.parentNode.removeChild(toRemove);
          }
        }
      }
    }
    
    // Run cleanup after DOM is fully loaded
    removeProblematicSections();
  }

  // Run immediately
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', cleanUpPage);
  } else {
    cleanUpPage();
  }
  
  // Also run after everything is loaded (for dynamically added content)
  window.addEventListener('load', cleanUpPage);
  
  // Run cleanup every second to catch any elements added dynamically
  setInterval(cleanUpPage, 1000);
})();
