"""
Performance monitoring system for tracking application metrics
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from collections import deque
import json
import os
from pathlib import Path

from app.config import settings


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    active_connections: int
    response_time_ms: Optional[float] = None
    request_count: int = 0
    error_count: int = 0


@dataclass
class DatabaseMetrics:
    """Database performance metrics"""
    timestamp: datetime
    query_count: int
    avg_query_time_ms: float
    slow_queries: int
    connection_pool_size: int
    active_connections: int
    total_forms: int
    pending_forms: int


class PerformanceMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self, max_history: int = 1000):
        """Initialize performance monitor"""
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.db_metrics_history: deque = deque(maxlen=max_history)
        self.request_times: deque = deque(maxlen=100)  # Last 100 requests
        self.query_times: deque = deque(maxlen=100)    # Last 100 queries
        
        self.monitoring_active = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # Performance counters
        self.request_counter = 0
        self.error_counter = 0
        self.query_counter = 0
        
        # Thresholds for alerts
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.response_time_threshold = 5000.0  # 5 seconds
        
        # Create metrics directory
        self.metrics_dir = Path("metrics")
        self.metrics_dir.mkdir(exist_ok=True)
    
    def start_monitoring(self, interval: int = 30):
        """Start background performance monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        print(f"📊 Performance monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("📊 Performance monitoring stopped")
    
    def _monitoring_loop(self, interval: int):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                metric = self._collect_system_metrics()
                
                with self.lock:
                    self.metrics_history.append(metric)
                
                # Collect database metrics
                db_metric = self._collect_database_metrics()
                if db_metric:
                    with self.lock:
                        self.db_metrics_history.append(db_metric)
                
                # Check for alerts
                self._check_performance_alerts(metric)
                
                # Save metrics to file periodically
                if len(self.metrics_history) % 10 == 0:
                    self._save_metrics_to_file()
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self) -> PerformanceMetric:
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Network connections (approximate active connections)
            connections = len(psutil.net_connections())
            
            # Calculate average response time from recent requests
            avg_response_time = None
            if self.request_times:
                avg_response_time = sum(self.request_times) / len(self.request_times)
            
            return PerformanceMetric(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                disk_usage_percent=disk_usage_percent,
                active_connections=connections,
                response_time_ms=avg_response_time,
                request_count=self.request_counter,
                error_count=self.error_counter
            )
            
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            return PerformanceMetric(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                disk_usage_percent=0.0,
                active_connections=0
            )
    
    def _collect_database_metrics(self) -> Optional[DatabaseMetrics]:
        """Collect database performance metrics"""
        try:
            # Import here to avoid circular import
            from app.database.connection import SessionLocal
            from app.database.crud import FormularioCRUD
            
            db = SessionLocal()
            
            # Calculate average query time
            avg_query_time = 0.0
            slow_queries = 0
            
            if self.query_times:
                avg_query_time = sum(self.query_times) / len(self.query_times)
                slow_queries = sum(1 for t in self.query_times if t > 1000)  # > 1 second
            
            # Get database statistics
            crud = FormularioCRUD(db)
            stats = crud.get_estadisticas_generales()
            
            db.close()
            
            return DatabaseMetrics(
                timestamp=datetime.utcnow(),
                query_count=self.query_counter,
                avg_query_time_ms=avg_query_time,
                slow_queries=slow_queries,
                connection_pool_size=settings.database_pool_size,
                active_connections=1,  # Simplified for SQLite
                total_forms=stats.get('total_formularios', 0),
                pending_forms=stats.get('pendientes', 0)
            )
            
        except Exception as e:
            print(f"Error collecting database metrics: {e}")
            return None
    
    def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check for performance alerts"""
        alerts = []
        
        if metric.cpu_percent > self.cpu_threshold:
            alerts.append(f"High CPU usage: {metric.cpu_percent:.1f}%")
        
        if metric.memory_percent > self.memory_threshold:
            alerts.append(f"High memory usage: {metric.memory_percent:.1f}%")
        
        if metric.response_time_ms and metric.response_time_ms > self.response_time_threshold:
            alerts.append(f"Slow response time: {metric.response_time_ms:.1f}ms")
        
        if alerts:
            print(f"⚠️  Performance Alert: {', '.join(alerts)}")
            self._log_alert(alerts)
    
    def _log_alert(self, alerts: List[str]):
        """Log performance alerts"""
        alert_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "alerts": alerts
        }
        
        alert_file = self.metrics_dir / "performance_alerts.jsonl"
        with open(alert_file, "a") as f:
            f.write(json.dumps(alert_data) + "\n")
    
    def _save_metrics_to_file(self):
        """Save metrics to file for persistence"""
        try:
            # Save system metrics
            metrics_file = self.metrics_dir / f"system_metrics_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
            
            with self.lock:
                recent_metrics = list(self.metrics_history)[-10:]  # Last 10 metrics
            
            with open(metrics_file, "a") as f:
                for metric in recent_metrics:
                    metric_dict = asdict(metric)
                    metric_dict['timestamp'] = metric.timestamp.isoformat()
                    f.write(json.dumps(metric_dict) + "\n")
            
            # Save database metrics
            if self.db_metrics_history:
                db_metrics_file = self.metrics_dir / f"db_metrics_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
                
                with self.lock:
                    recent_db_metrics = list(self.db_metrics_history)[-10:]
                
                with open(db_metrics_file, "a") as f:
                    for metric in recent_db_metrics:
                        metric_dict = asdict(metric)
                        metric_dict['timestamp'] = metric.timestamp.isoformat()
                        f.write(json.dumps(metric_dict) + "\n")
                        
        except Exception as e:
            print(f"Error saving metrics to file: {e}")
    
    def record_request(self, response_time_ms: float, is_error: bool = False):
        """Record a request with its response time"""
        with self.lock:
            self.request_counter += 1
            if is_error:
                self.error_counter += 1
            
            self.request_times.append(response_time_ms)
    
    def record_query(self, query_time_ms: float):
        """Record a database query with its execution time"""
        with self.lock:
            self.query_counter += 1
            self.query_times.append(query_time_ms)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        try:
            current_metric = self._collect_system_metrics()
            current_db_metric = self._collect_database_metrics()
            
            return {
                "system": asdict(current_metric),
                "database": asdict(current_db_metric) if current_db_metric else None,
                "summary": {
                    "total_requests": self.request_counter,
                    "total_errors": self.error_counter,
                    "error_rate": (self.error_counter / max(self.request_counter, 1)) * 100,
                    "avg_response_time": sum(self.request_times) / len(self.request_times) if self.request_times else 0,
                    "total_queries": self.query_counter,
                    "avg_query_time": sum(self.query_times) / len(self.query_times) if self.query_times else 0
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_metrics_history(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics history for the specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            # Filter metrics by time
            recent_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= cutoff_time
            ]
            
            recent_db_metrics = [
                m for m in self.db_metrics_history 
                if m.timestamp >= cutoff_time
            ]
        
        return {
            "system_metrics": [asdict(m) for m in recent_metrics],
            "database_metrics": [asdict(m) for m in recent_db_metrics],
            "period_hours": hours,
            "total_points": len(recent_metrics)
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        with self.lock:
            recent_metrics = list(self.metrics_history)[-100:]  # Last 100 metrics
        
        if not recent_metrics:
            return {"error": "No recent metrics available"}
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        
        # Calculate average response time safely
        response_times = [m.response_time_ms for m in recent_metrics if m.response_time_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Find peaks
        max_cpu = max(m.cpu_percent for m in recent_metrics)
        max_memory = max(m.memory_percent for m in recent_metrics)
        max_response_time = max(response_times) if response_times else 0
        
        return {
            "averages": {
                "cpu_percent": round(avg_cpu, 2),
                "memory_percent": round(avg_memory, 2),
                "response_time_ms": round(avg_response_time, 2) if avg_response_time else 0
            },
            "peaks": {
                "max_cpu_percent": round(max_cpu, 2),
                "max_memory_percent": round(max_memory, 2),
                "max_response_time_ms": round(max_response_time, 2)
            },
            "totals": {
                "total_requests": self.request_counter,
                "total_errors": self.error_counter,
                "total_queries": self.query_counter
            },
            "health_status": self._get_health_status(avg_cpu, avg_memory, avg_response_time)
        }
    
    def _get_health_status(self, avg_cpu: float, avg_memory: float, avg_response_time: float) -> str:
        """Determine overall health status"""
        if avg_cpu > 80 or avg_memory > 85 or (avg_response_time and avg_response_time > 3000):
            return "critical"
        elif avg_cpu > 60 or avg_memory > 70 or (avg_response_time and avg_response_time > 2000):
            return "warning"
        else:
            return "healthy"
    
    def cleanup_old_metrics(self, days_to_keep: int = 7):
        """Clean up old metric files"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for file_path in self.metrics_dir.glob("*.jsonl"):
            try:
                # Extract date from filename
                date_str = file_path.stem.split('_')[-1]
                file_date = datetime.strptime(date_str, '%Y%m%d')
                
                if file_date < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
                    
            except (ValueError, IndexError):
                # Skip files that don't match the expected format
                continue
        
        print(f"🧹 Cleaned up {deleted_count} old metric files")
        return deleted_count


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


class PerformanceMiddleware:
    """Middleware to track request performance"""
    
    def __init__(self):
        self.monitor = performance_monitor
    
    def __call__(self, func):
        """Decorator to track function performance"""
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
                response_time_ms = (end_time - start_time) * 1000
                self.monitor.record_request(response_time_ms, error_occurred)
        
        return wrapper


# Decorator for easy use
def monitor_performance(func):
    """Decorator to monitor function performance"""
    middleware = PerformanceMiddleware()
    return middleware(func)