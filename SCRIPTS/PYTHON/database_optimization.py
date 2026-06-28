"""
Database Query Optimization and Caching Strategies for AUGGDASH26 Dashboard System
This module implements optimized database queries and advanced caching strategies
to improve performance of the dashboard system.
"""

import time
import functools
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
import redis
import sqlite3
from contextlib import contextmanager

# Redis connection for caching
class CacheManager:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        self.default_ttl = 3600  # 1 hour default TTL
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            return self.redis_client.get(key)
        except redis.RedisError:
            return None
    
    def set(self, key: str, value: str, ttl: int = None) -> bool:
        """Set value in cache with optional TTL"""
        try:
            ttl = ttl or self.default_ttl
            return self.redis_client.setex(key, ttl, value)
        except redis.RedisError:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError:
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except redis.RedisError:
            return 0
    
    def get_hash(self, key: str, field: str) -> Optional[str]:
        """Get field from hash in cache"""
        try:
            return self.redis_client.hget(key, field)
        except redis.RedisError:
            return None
    
    def set_hash(self, key: str, field: str, value: str, ttl: int = None) -> bool:
        """Set field in hash in cache"""
        try:
            result = self.redis_client.hset(key, field, value)
            # Set expiration if TTL is provided
            if ttl:
                self.redis_client.expire(key, ttl)
            return bool(result)
        except redis.RedisError:
            return False

# Database connection manager with connection pooling
class DatabaseManager:
    def __init__(self, db_path: str, pool_size: int = 10):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connections = []
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize database connection pool"""
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            self.connections.append(conn)
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        if self.connections:
            conn = self.connections.pop()
            try:
                yield conn
            finally:
                # Return connection to pool
                self.connections.append(conn)
        else:
            # If pool is empty, create a temporary connection
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query with connection pooling"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

# Query optimization utilities
class QueryOptimizer:
    @staticmethod
    def add_indexes(db_manager: DatabaseManager):
        """Add indexes to improve query performance"""
        indexes = [
            # Dashboard indexes
            "CREATE INDEX IF NOT EXISTS idx_dashboard_category ON dashboards(category);",
            "CREATE INDEX IF NOT EXISTS idx_dashboard_created ON dashboards(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_dashboard_updated ON dashboards(updated_at);",
            "CREATE INDEX IF NOT EXISTS idx_dashboard_status ON dashboards(status);",
            
            # User indexes
            "CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_user_role ON users(role);",
            
            # Analytics indexes
            "CREATE INDEX IF NOT EXISTS idx_analytics_dashboard_id ON analytics(dashboard_id);",
            "CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp);",
        ]
        
        for index_query in indexes:
            try:
                db_manager.execute_update(index_query)
            except sqlite3.Error as e:
                print(f"Error creating index: {e}")
    
    @staticmethod
    def optimize_dashboard_query(category: str = None, limit: int = 50, offset: int = 0) -> tuple:
        """Optimized query for fetching dashboards with optional filtering"""
        base_query = """
            SELECT d.id, d.name, d.category, d.description, d.created_at, d.updated_at, d.status,
                   COUNT(a.id) as view_count
            FROM dashboards d
            LEFT JOIN analytics a ON d.id = a.dashboard_id
            WHERE 1=1
        """
        
        params = []
        
        if category:
            base_query += " AND d.category = ?"
            params.append(category)
        
        base_query += """
            GROUP BY d.id
            ORDER BY d.updated_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        return base_query, tuple(params)
    
    @staticmethod
    def optimize_search_query(search_term: str, category: str = None) -> tuple:
        """Optimized query for searching dashboards"""
        base_query = """
            SELECT d.id, d.name, d.category, d.description, d.created_at, d.updated_at,
                   COUNT(a.id) as view_count
            FROM dashboards d
            LEFT JOIN analytics a ON d.id = a.dashboard_id
            WHERE d.name LIKE ? OR d.description LIKE ?
        """
        
        params = [f'%{search_term}%', f'%{search_term}%']
        
        if category:
            base_query += " AND d.category = ?"
            params.append(category)
        
        base_query += " GROUP BY d.id ORDER BY d.updated_at DESC"
        
        return base_query, tuple(params)

# Caching decorator
def cached(ttl: int = 3600, key_prefix: str = "cache"):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cache_manager = CacheManager()
            cached_result = cache_manager.get(cache_key)
            
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, json.dumps(result), ttl)
            
            return result
        return wrapper
    return decorator

# Dashboard service with optimized queries and caching
class DashboardService:
    def __init__(self, db_manager: DatabaseManager, cache_manager: CacheManager):
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.query_optimizer = QueryOptimizer()
        
        # Add indexes for better performance
        self.query_optimizer.add_indexes(db_manager)
    
    @cached(ttl=1800, key_prefix="dashboard_list")  # Cache for 30 minutes
    def get_dashboards(self, category: str = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get dashboards with caching and optimized queries"""
        query, params = self.query_optimizer.optimize_dashboard_query(category, limit, offset)
        rows = self.db_manager.execute_query(query, params)
        
        return [dict(row) for row in rows]
    
    @cached(ttl=3600, key_prefix="dashboard_detail")  # Cache for 1 hour
    def get_dashboard_by_id(self, dashboard_id: int) -> Optional[Dict]:
        """Get a specific dashboard by ID"""
        query = """
            SELECT d.*, u.username as owner_name
            FROM dashboards d
            LEFT JOIN users u ON d.user_id = u.id
            WHERE d.id = ?
        """
        rows = self.db_manager.execute_query(query, (dashboard_id,))
        
        if rows:
            return dict(rows[0])
        return None
    
    @cached(ttl=900, key_prefix="search_results")  # Cache for 15 minutes
    def search_dashboards(self, search_term: str, category: str = None) -> List[Dict]:
        """Search dashboards with caching"""
        query, params = self.query_optimizer.optimize_search_query(search_term, category)
        rows = self.db_manager.execute_query(query, params)
        
        return [dict(row) for row in rows]
    
    def get_dashboard_analytics(self, dashboard_id: int, days: int = 30) -> Dict:
        """Get analytics for a dashboard with caching"""
        cache_key = f"analytics:{dashboard_id}:{days}"
        cached_result = self.cache_manager.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Calculate date threshold
        threshold_date = datetime.now() - timedelta(days=days)
        
        # Query analytics data
        query = """
            SELECT 
                COUNT(*) as total_views,
                COUNT(DISTINCT user_id) as unique_users,
                AVG(session_duration) as avg_session_duration,
                strftime('%Y-%m-%d', timestamp) as date,
                COUNT(*) as daily_views
            FROM analytics
            WHERE dashboard_id = ? AND timestamp >= ?
            GROUP BY date
            ORDER BY date DESC
        """
        
        rows = self.db_manager.execute_query(query, (dashboard_id, threshold_date.isoformat()))
        result = {
            'total_views': 0,
            'unique_users': 0,
            'avg_session_duration': 0,
            'daily_breakdown': [dict(row) for row in rows]
        }
        
        # Calculate aggregates
        if rows:
            result['total_views'] = sum(row['total_views'] for row in rows)
            result['unique_users'] = sum(row['unique_users'] for row in rows)
            durations = [row['avg_session_duration'] for row in rows if row['avg_session_duration']]
            if durations:
                result['avg_session_duration'] = sum(durations) / len(durations)
        
        # Cache the result
        self.cache_manager.set(cache_key, json.dumps(result), 1800)  # Cache for 30 minutes
        
        return result
    
    def invalidate_dashboard_cache(self, dashboard_id: int):
        """Invalidate cache for a specific dashboard"""
        # Invalidate dashboard detail cache
        self.cache_manager.invalidate_pattern(f"dashboard_detail:*{dashboard_id}*")
        
        # Invalidate related analytics cache
        self.cache_manager.invalidate_pattern(f"analytics:{dashboard_id}:*")

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def time_function(self, name: str = None):
        """Decorator to time function execution"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                execution_time = end_time - start_time
                func_name = name or func.__name__
                
                # Store metrics
                if func_name not in self.metrics:
                    self.metrics[func_name] = []
                self.metrics[func_name].append(execution_time)
                
                print(f"{func_name} executed in {execution_time:.4f}s")
                
                return result
            return wrapper
        return decorator
    
    def get_average_execution_time(self, func_name: str) -> float:
        """Get average execution time for a function"""
        if func_name in self.metrics and self.metrics[func_name]:
            times = self.metrics[func_name]
            return sum(times) / len(times)
        return 0.0
    
    def get_slow_queries(self, threshold: float = 1.0) -> Dict[str, float]:
        """Get functions that take longer than threshold"""
        slow_functions = {}
        for func_name, times in self.metrics.items():
            avg_time = sum(times) / len(times)
            if avg_time > threshold:
                slow_functions[func_name] = avg_time
        return slow_functions

# Example usage and initialization
def initialize_optimization_system():
    """Initialize the optimization system"""
    # Initialize database manager
    db_manager = DatabaseManager("dashboards.db")
    
    # Initialize cache manager
    cache_manager = CacheManager()
    
    # Initialize dashboard service
    dashboard_service = DashboardService(db_manager, cache_manager)
    
    # Initialize performance monitor
    performance_monitor = PerformanceMonitor()
    
    return {
        'db_manager': db_manager,
        'cache_manager': cache_manager,
        'dashboard_service': dashboard_service,
        'performance_monitor': performance_monitor
    }

# Example of how to use the optimized system
if __name__ == "__main__":
    # Initialize the optimization system
    optimization_system = initialize_optimization_system()
    
    print("Database query optimization and caching system initialized")
    print(f"Cache connected: {optimization_system['cache_manager'].redis_client.ping()}")
    
    # Example of using the dashboard service
    dashboard_service = optimization_system['dashboard_service']
    
    # Get dashboards (this will be cached)
    dashboards = dashboard_service.get_dashboards(limit=10)
    print(f"Retrieved {len(dashboards)} dashboards")
    
    # Performance monitoring example
    monitor = optimization_system['performance_monitor']
    
    @monitor.time_function("example_query")
    def example_query():
        time.sleep(0.1)  # Simulate some work
        return "result"
    
    result = example_query()
    avg_time = monitor.get_average_execution_time("example_query")
    print(f"Average execution time for example_query: {avg_time:.4f}s")