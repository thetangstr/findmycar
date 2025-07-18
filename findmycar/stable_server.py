#!/usr/bin/env python3
"""Stable server startup with crash detection and recovery."""

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
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StableServer:
    def __init__(self):
        self.process = None
        self.restart_count = 0
        self.max_restarts = 5
        
    def start_server(self):
        """Start the FastAPI server."""
        try:
            logger.info("🚀 Starting FastAPI server...")
            
            # Kill any existing processes on port 8601
            os.system("lsof -ti :8601 | xargs kill -9 2>/dev/null || true")
            time.sleep(2)
            
            # Start server with proper error handling
            cmd = [
                sys.executable, "-c",
                """
import uvicorn
import main
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        main.app, 
        host="127.0.0.1", 
        port=8601, 
        log_level="info",
        access_log=True
    )
except Exception as e:
    logger.error(f"Server error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
                """
            ]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Wait a moment for startup
            time.sleep(3)
            
            # Check if process is still running
            if self.process.poll() is None:
                logger.info("✅ Server started successfully")
                return True
            else:
                logger.error("❌ Server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting server: {e}")
            return False
    
    def monitor_server(self):
        """Monitor server and restart if it crashes."""
        logger.info("🔍 Starting server monitoring...")
        
        while self.restart_count < self.max_restarts:
            if not self.start_server():
                logger.error("Failed to start server")
                break
                
            # Monitor the process
            while self.process and self.process.poll() is None:
                time.sleep(5)  # Check every 5 seconds
                
                # Test if server is responding
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:8601/", timeout=5)
                    if response.status_code != 200:
                        logger.warning("Server not responding properly")
                except:
                    logger.warning("Server health check failed")
                    break
            
            # Server crashed
            self.restart_count += 1
            logger.error(f"💥 Server crashed! Restart attempt {self.restart_count}/{self.max_restarts}")
            
            if self.restart_count < self.max_restarts:
                logger.info("⏰ Waiting 10 seconds before restart...")
                time.sleep(10)
            else:
                logger.error("❌ Max restarts reached. Giving up.")
                break
    
    def stop_server(self):
        """Stop the server gracefully."""
        if self.process:
            logger.info("🛑 Stopping server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Force killing server...")
                self.process.kill()

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("🛑 Received shutdown signal")
    server.stop_server()
    sys.exit(0)

if __name__ == "__main__":
    server = StableServer()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        server.monitor_server()
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    finally:
        server.stop_server()