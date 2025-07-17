#!/usr/bin/env python3
"""
Parallel ingestion system for improved search performance
"""

import asyncio
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable, Any
from sqlalchemy.orm import Session
from database import SessionLocal
from performance_profiler import PerformanceTimer

logger = logging.getLogger(__name__)

class ParallelIngestionManager:
    """Manages parallel execution of multiple source ingestions"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)
    
    def ingest_source(self, source_name: str, ingest_func: Callable, 
                     query: str, filters: Dict = None, limit: int = 50, session_id: str = None) -> Dict:
        """Execute a single source ingestion with its own database session"""
        
        with PerformanceTimer(f"parallel_ingestion.{source_name}"):
            try:
                # Create a new database session for this thread
                db = SessionLocal()
                
                logger.info(f"🚀 Starting parallel ingestion for {source_name}")
                start_time = time.time()
                
                # Send progress update if session_id provided
                if session_id:
                    try:
                        import asyncio
                        from websocket_progress import progress_manager
                        # Create new event loop for this thread
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            progress_manager.update_source_progress(session_id, source_name, "starting")
                        )
                        loop.close()
                    except Exception as e:
                        logger.error(f"Failed to send progress update: {e}")
                
                # Call the source-specific ingestion function
                result = ingest_func(db, query, filters, limit)
                
                elapsed_time = time.time() - start_time
                logger.info(f"✅ {source_name} completed in {elapsed_time:.2f}s")
                
                # Send completion update
                if session_id:
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            progress_manager.update_source_progress(session_id, source_name, "completed", {
                                "ingested": result.get('ingested', 0),
                                "skipped": result.get('skipped', 0),
                                "errors": result.get('errors', 0),
                                "elapsed_time": elapsed_time
                            })
                        )
                        loop.close()
                    except Exception as e:
                        logger.error(f"Failed to send completion update: {e}")
                
                # Add timing info to result
                result['elapsed_time'] = elapsed_time
                result['source_name'] = source_name
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Error in {source_name} ingestion: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'source_name': source_name,
                    'ingested': 0,
                    'skipped': 0,
                    'errors': 1
                }
            finally:
                db.close()
    
    def ingest_all_sources_parallel(self, source_configs: List[Dict], 
                                  query: str, filters: Dict = None, session_id: str = None) -> Dict:
        """
        Ingest from multiple sources in parallel
        
        Args:
            source_configs: List of dicts with 'name' and 'function' keys
            query: Search query
            filters: Optional filters
            
        Returns:
            Combined results from all sources
        """
        
        with PerformanceTimer("parallel_ingestion.total"):
            start_time = time.time()
            futures = {}
            
            # Submit all ingestion tasks
            for config in source_configs:
                source_name = config['name']
                ingest_func = config['function']
                limit = config.get('limit', 50)
                
                future = self.executor.submit(
                    self.ingest_source,
                    source_name,
                    ingest_func,
                    query,
                    filters,
                    limit,
                    session_id
                )
                futures[future] = source_name
            
            # Collect results as they complete
            results = {
                'success': True,
                'total_ingested': 0,
                'total_skipped': 0,
                'total_errors': 0,
                'sources': {},
                'elapsed_time': 0
            }
            
            completed_count = 0
            total_sources = len(futures)
            
            for future in as_completed(futures):
                source_name = futures[future]
                completed_count += 1
                
                try:
                    result = future.result()
                    
                    # Update totals
                    results['total_ingested'] += result.get('ingested', 0)
                    results['total_skipped'] += result.get('skipped', 0)
                    results['total_errors'] += result.get('errors', 0)
                    
                    # Store source-specific results
                    results['sources'][source_name] = result
                    
                    # Log progress
                    logger.info(f"📊 Progress: {completed_count}/{total_sources} sources completed")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to get result for {source_name}: {e}")
                    results['sources'][source_name] = {
                        'success': False,
                        'error': str(e),
                        'ingested': 0,
                        'skipped': 0,
                        'errors': 1
                    }
            
            # Calculate total elapsed time
            results['elapsed_time'] = time.time() - start_time
            
            # Log summary
            logger.info(f"🎯 Parallel ingestion completed in {results['elapsed_time']:.2f}s")
            logger.info(f"📈 Total ingested: {results['total_ingested']} vehicles")
            logger.info(f"⏱️  Time saved: ~{self._estimate_time_saved(results)}s")
            
            return results
    
    def _estimate_time_saved(self, results: Dict) -> float:
        """Estimate time saved by parallel execution"""
        sequential_time = sum(
            source_result.get('elapsed_time', 0) 
            for source_result in results['sources'].values()
        )
        parallel_time = results['elapsed_time']
        return max(0, sequential_time - parallel_time)


# Update the multi-source ingestion function to use parallel execution
def ingest_multi_source_parallel(db: Session, query: str, filters=None, sources=None, session_id=None):
    """
    Enhanced multi-source ingestion with parallel execution
    """
    from ingestion import (
        ingest_data, ingest_carmax_data, ingest_bat_data,
        ingest_cargurus_data, ingest_autotrader_data
    )
    
    if not sources:
        sources = ['ebay']
    
    # Map source names to ingestion functions
    source_mapping = {
        'ebay': ingest_data,
        'carmax': ingest_carmax_data,
        'bringatrailer': ingest_bat_data,
        'cargurus': ingest_cargurus_data,
        'autotrader': ingest_autotrader_data
    }
    
    # Build source configurations
    source_configs = []
    for source in sources:
        if source in source_mapping:
            source_configs.append({
                'name': source,
                'function': source_mapping[source],
                'limit': 25  # Limit per source for faster results
            })
    
    # Use parallel ingestion
    with ParallelIngestionManager(max_workers=5) as manager:
        results = manager.ingest_all_sources_parallel(source_configs, query, filters, session_id)
    
    return results