#!/usr/bin/env python3
"""
WebDriver pool for reusing Selenium instances across requests
"""

import logging
from queue import Queue, Empty
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import atexit
import threading

logger = logging.getLogger(__name__)

class WebDriverPool:
    """Pool of reusable WebDriver instances"""
    
    def __init__(self, pool_size: int = 3):
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self.drivers = []
        
        # Create initial drivers
        self._initialize_pool()
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def _create_driver(self) -> webdriver.Chrome:
        """Create a new Chrome driver with optimized settings"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Performance optimizations
        chrome_options.add_argument("--disable-images")  # Don't load images
        chrome_options.add_argument("--disable-javascript")  # Disable JS for faster loading
        chrome_options.add_experimental_option('prefs', {
            'profile.managed_default_content_settings.images': 2,  # Block images
            'profile.default_content_setting_values.notifications': 2,  # Block notifications
        })
        
        # Anti-detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _initialize_pool(self):
        """Initialize the driver pool"""
        logger.info(f"🚀 Initializing WebDriver pool with {self.pool_size} drivers")
        
        for i in range(self.pool_size):
            try:
                driver = self._create_driver()
                self.drivers.append(driver)
                self.pool.put(driver)
                logger.debug(f"Created driver {i+1}/{self.pool_size}")
            except Exception as e:
                logger.error(f"Failed to create driver {i+1}: {e}")
    
    def get_driver(self, timeout: float = 5.0) -> webdriver.Chrome:
        """Get a driver from the pool"""
        try:
            driver = self.pool.get(timeout=timeout)
            logger.debug("Got driver from pool")
            return driver
        except Empty:
            logger.warning("Driver pool exhausted, creating new driver")
            return self._create_driver()
    
    def return_driver(self, driver: webdriver.Chrome):
        """Return a driver to the pool"""
        try:
            # Clear cookies and reset state
            driver.delete_all_cookies()
            driver.get("about:blank")
            
            # Return to pool if there's space
            if self.pool.qsize() < self.pool_size:
                self.pool.put(driver)
                logger.debug("Returned driver to pool")
            else:
                # Pool is full, close the driver
                driver.quit()
                logger.debug("Pool full, closed extra driver")
        except Exception as e:
            logger.error(f"Error returning driver to pool: {e}")
            try:
                driver.quit()
            except:
                pass
    
    def cleanup(self):
        """Clean up all drivers"""
        logger.info("🧹 Cleaning up WebDriver pool")
        
        # Close all drivers in the pool
        while not self.pool.empty():
            try:
                driver = self.pool.get_nowait()
                driver.quit()
            except:
                pass
        
        # Close any tracked drivers
        for driver in self.drivers:
            try:
                driver.quit()
            except:
                pass

# Global driver pool instance
driver_pool = WebDriverPool(pool_size=3)