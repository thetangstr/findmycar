"""WebSocket-based real-time progress tracking for search operations."""

import asyncio
import json
import logging
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

class ProgressManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.search_progress: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a WebSocket client."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        """Disconnect a WebSocket client."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.search_progress:
            del self.search_progress[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_progress(self, session_id: str, progress_data: Dict):
        """Send progress update to a specific client."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(progress_data))
            except Exception as e:
                logger.error(f"Error sending progress to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def broadcast_progress(self, progress_data: Dict):
        """Broadcast progress to all connected clients."""
        disconnected = []
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(progress_data))
            except Exception as e:
                logger.error(f"Error broadcasting to {session_id}: {e}")
                disconnected.append(session_id)
        
        # Clean up disconnected clients
        for session_id in disconnected:
            self.disconnect(session_id)
    
    def start_search(self, session_id: str, query: str, sources: List[str]):
        """Initialize search progress tracking."""
        self.search_progress[session_id] = {
            "query": query,
            "sources": sources,
            "total_sources": len(sources),
            "completed_sources": 0,
            "current_source": None,
            "status": "starting",
            "start_time": datetime.now().isoformat(),
            "results": {},
            "errors": []
        }
    
    async def update_source_progress(self, session_id: str, source: str, status: str, details: Dict = None):
        """Update progress for a specific source."""
        if session_id not in self.search_progress:
            return
            
        progress = self.search_progress[session_id]
        progress["current_source"] = source
        progress["status"] = status
        
        if details:
            progress["results"][source] = details
        
        if status == "completed":
            progress["completed_sources"] += 1
            if progress["completed_sources"] >= progress["total_sources"]:
                progress["status"] = "finished"
                progress["end_time"] = datetime.now().isoformat()
        
        # Send update to client
        await self.send_progress(session_id, {
            "type": "search_progress",
            "data": progress
        })
    
    async def add_error(self, session_id: str, source: str, error: str):
        """Add error to search progress."""
        if session_id not in self.search_progress:
            return
            
        self.search_progress[session_id]["errors"].append({
            "source": source,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        await self.send_progress(session_id, {
            "type": "search_error",
            "data": {
                "source": source,
                "error": error
            }
        })

# Global progress manager instance
progress_manager = ProgressManager()