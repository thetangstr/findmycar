#!/usr/bin/env python3
"""
Stable Flask server launcher with monitoring.
Alternative to FastAPI for better stability.
"""

import os
import sys
import time
import signal
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StableFlaskServer:
    def __init__(self):
        self.process = None
        self.restart_count = 0
        self.max_restarts = 3
        
    def start_server(self):
        """Start the Flask server."""
        try:
            logger.info("🚀 Starting Flask server...")
            
            # Kill any existing processes on port 8601
            os.system("lsof -ti :8601 | xargs kill -9 2>/dev/null || true")
            time.sleep(2)
            
            # Start Flask server
            self.process = subprocess.Popen(
                [sys.executable, "flask_app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Wait for startup
            time.sleep(3)
            
            # Check if process is still running
            if self.process.poll() is None:
                logger.info("✅ Flask server started successfully")
                return True
            else:
                logger.error("❌ Flask server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Flask server: {e}")
            return False
    
    def monitor_server(self):
        """Monitor Flask server and restart if it crashes."""
        logger.info("🔍 Starting Flask server monitoring...")
        
        while self.restart_count < self.max_restarts:
            if not self.start_server():
                logger.error("Failed to start Flask server")
                break
                
            # Monitor the process
            while self.process and self.process.poll() is None:
                time.sleep(10)  # Check every 10 seconds
                
                # Test if server is responding
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:8601/health", timeout=5)
                    if response.status_code == 200:
                        logger.debug("✅ Flask server health check passed")
                    else:
                        logger.warning("⚠️ Flask server health check failed")
                        break
                except Exception as e:
                    logger.warning(f"⚠️ Flask server health check failed: {e}")
                    break
            
            # Server crashed
            self.restart_count += 1
            logger.error(f"💥 Flask server crashed! Restart attempt {self.restart_count}/{self.max_restarts}")
            
            if self.restart_count < self.max_restarts:
                logger.info("⏰ Waiting 5 seconds before restart...")
                time.sleep(5)
            else:
                logger.error("❌ Max restarts reached. Giving up.")
                break
    
    def stop_server(self):
        """Stop the Flask server gracefully."""
        if self.process:
            logger.info("🛑 Stopping Flask server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Force killing Flask server...")
                self.process.kill()

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("🛑 Received shutdown signal")
    server.stop_server()
    sys.exit(0)

if __name__ == "__main__":
    server = StableFlaskServer()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        server.monitor_server()
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    finally:
        server.stop_server()