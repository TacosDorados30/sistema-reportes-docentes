"""
Database monitoring middleware
"""

import time
import functools
from typing import Any, Callable
from sqlalchemy import event
from sqlalchemy.engine import Engine


class DatabaseMonitor:
    """Monitor database operations"""
    
    def __init__(self):
        self.query_start_times = {}
    
    def setup_monitoring(self, engine: Engine):
        """Set up database monitoring events"""
        
        @event.listens_for(engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Record query start time"""
            context._query_start_time = time.time()
        
        @event.listens_for(engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Record query completion and duration"""
            if hasattr(context, '_query_start_time'):
                query_time = (time.time() - context._query_start_time) * 1000  # Convert to ms
                
                # Import here to avoid circular import
                try:
                    from app.core.performance_monitor import performance_monitor
                    performance_monitor.record_query(query_time)
                except ImportError:
                    pass  # Performance monitoring not available
                
                # Log slow queries
                if query_time > 1000:  # Queries slower than 1 second
                    print(f"⚠️ Slow query detected: {query_time:.2f}ms")
                    print(f"Statement: {statement[:100]}...")


def monitor_database_operation(func: Callable) -> Callable:
    """Decorator to monitor database operations"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        error_occurred = False
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_occurred = True
            raise e
        finally:
            end_time = time.time()
            operation_time_ms = (end_time - start_time) * 1000
            
            # Record as a request (database operation)
            try:
                from app.core.performance_monitor import performance_monitor
                performance_monitor.record_request(operation_time_ms, error_occurred)
            except ImportError:
                pass  # Performance monitoring not available
    
    return wrapper


# Global database monitor instance
db_monitor = DatabaseMonitor()