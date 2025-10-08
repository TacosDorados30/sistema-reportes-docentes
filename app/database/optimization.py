"""
Database optimization utilities
"""

from sqlalchemy import text, Index
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import time

from app.database.connection import SessionLocal, engine
from app.core.logging_middleware import app_logger

class DatabaseOptimizer:
    """Database optimization and performance monitoring"""
    
    def __init__(self):
        self.query_stats = {}
    
    def create_indexes(self):
        """Create performance indexes"""
        
        indexes_to_create = [
            # Formularios indexes
            "CREATE INDEX IF NOT EXISTS idx_formularios_estado ON formularios_envio(estado)",
            "CREATE INDEX IF NOT EXISTS idx_formularios_fecha_envio ON formularios_envio(fecha_envio)",
            "CREATE INDEX IF NOT EXISTS idx_formularios_correo ON formularios_envio(correo_institucional)",
            
            # Cursos indexes
            "CREATE INDEX IF NOT EXISTS idx_cursos_formulario_id ON cursos_capacitacion(formulario_id)",
            "CREATE INDEX IF NOT EXISTS idx_cursos_fecha ON cursos_capacitacion(fecha)",
            
            # Publicaciones indexes
            "CREATE INDEX IF NOT EXISTS idx_publicaciones_formulario_id ON publicaciones(formulario_id)",
            "CREATE INDEX IF NOT EXISTS idx_publicaciones_estatus ON publicaciones(estatus)",
            
            # Eventos indexes
            "CREATE INDEX IF NOT EXISTS idx_eventos_formulario_id ON eventos_academicos(formulario_id)",
            "CREATE INDEX IF NOT EXISTS idx_eventos_fecha ON eventos_academicos(fecha)",
            
            # Audit logs indexes (already created in model, but ensuring they exist)
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_severity ON audit_logs(severity)",
        ]
        
        db = SessionLocal()
        try:
            for index_sql in indexes_to_create:
                try:
                    db.execute(text(index_sql))
                    app_logger.log_database_operation(
                        "CREATE_INDEX",
                        table=index_sql.split(" ON ")[1].split("(")[0] if " ON " in index_sql else "unknown"
                    )
                except Exception as e:
                    app_logger.log_operation(
                        f"index_creation_failed",
                        {"sql": index_sql, "error": str(e)},
                        "WARNING"
                    )
            
            db.commit()
            app_logger.log_operation("database_indexes_created", {"count": len(indexes_to_create)})
            
        except Exception as e:
            db.rollback()
            app_logger.log_operation(
                "database_index_creation_failed",
                {"error": str(e)},
                "ERROR"
            )
        finally:
            db.close()
    
    def analyze_tables(self):
        """Analyze tables for query optimization (SQLite specific)"""
        
        tables_to_analyze = [
            "formularios_envio",
            "cursos_capacitacion", 
            "publicaciones",
            "eventos_academicos",
            "audit_logs"
        ]
        
        db = SessionLocal()
        try:
            for table in tables_to_analyze:
                try:
                    db.execute(text(f"ANALYZE {table}"))
                    app_logger.log_database_operation("ANALYZE", table=table)
                except Exception as e:
                    app_logger.log_operation(
                        f"table_analysis_failed",
                        {"table": table, "error": str(e)},
                        "WARNING"
                    )
            
            db.commit()
            app_logger.log_operation("database_tables_analyzed", {"count": len(tables_to_analyze)})
            
        except Exception as e:
            db.rollback()
            app_logger.log_operation(
                "database_analysis_failed",
                {"error": str(e)},
                "ERROR"
            )
        finally:
            db.close()
    
    def get_query_performance_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        
        db = SessionLocal()
        try:
            # Get table sizes
            table_stats = {}
            tables = ["formularios_envio", "cursos_capacitacion", "publicaciones", 
                     "eventos_academicos", "audit_logs"]
            
            for table in tables:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) as count FROM {table}")).fetchone()
                    table_stats[table] = {"row_count": result[0] if result else 0}
                except Exception as e:
                    table_stats[table] = {"error": str(e)}
            
            # Get index usage (SQLite specific)
            try:
                indexes_result = db.execute(text("""
                    SELECT name, tbl_name 
                    FROM sqlite_master 
                    WHERE type = 'index' 
                    AND name NOT LIKE 'sqlite_%'
                """)).fetchall()
                
                indexes = [{"name": row[0], "table": row[1]} for row in indexes_result]
            except Exception as e:
                indexes = []
            
            return {
                "table_statistics": table_stats,
                "indexes": indexes,
                "query_stats": self.query_stats
            }
            
        except Exception as e:
            app_logger.log_operation(
                "performance_stats_failed",
                {"error": str(e)},
                "ERROR"
            )
            return {"error": str(e)}
        finally:
            db.close()
    
    def optimize_database(self):
        """Run full database optimization"""
        
        start_time = time.time()
        
        try:
            app_logger.log_operation("database_optimization_started")
            
            # Create indexes
            self.create_indexes()
            
            # Analyze tables
            self.analyze_tables()
            
            # Vacuum database (SQLite specific)
            self.vacuum_database()
            
            duration = time.time() - start_time
            app_logger.log_performance(
                "database_optimization",
                duration,
                {"status": "completed"}
            )
            
        except Exception as e:
            duration = time.time() - start_time
            app_logger.log_performance(
                "database_optimization",
                duration,
                {"status": "failed", "error": str(e)}
            )
            raise
    
    def vacuum_database(self):
        """Vacuum database to reclaim space and optimize"""
        
        try:
            # Use raw connection for VACUUM (can't be in transaction)
            with engine.connect() as conn:
                conn.execute(text("VACUUM"))
                conn.commit()
            
            app_logger.log_database_operation("VACUUM")
            
        except Exception as e:
            app_logger.log_operation(
                "database_vacuum_failed",
                {"error": str(e)},
                "WARNING"
            )
    
    def monitor_query(self, query_name: str, duration: float, row_count: int = None):
        """Monitor query performance"""
        
        if query_name not in self.query_stats:
            self.query_stats[query_name] = {
                "count": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "max_duration": 0,
                "min_duration": float('inf')
            }
        
        stats = self.query_stats[query_name]
        stats["count"] += 1
        stats["total_duration"] += duration
        stats["avg_duration"] = stats["total_duration"] / stats["count"]
        stats["max_duration"] = max(stats["max_duration"], duration)
        stats["min_duration"] = min(stats["min_duration"], duration)
        
        if row_count is not None:
            if "total_rows" not in stats:
                stats["total_rows"] = 0
                stats["avg_rows"] = 0
            stats["total_rows"] += row_count
            stats["avg_rows"] = stats["total_rows"] / stats["count"]
        
        # Log slow queries
        if duration > 1.0:  # Queries taking more than 1 second
            app_logger.log_operation(
                f"slow_query_{query_name}",
                {"duration": duration, "row_count": row_count},
                "WARNING"
            )

# Global optimizer instance
db_optimizer = DatabaseOptimizer()

def optimize_database():
    """Run database optimization"""
    return db_optimizer.optimize_database()

def get_performance_stats():
    """Get database performance statistics"""
    return db_optimizer.get_query_performance_stats()

def monitor_query_performance(query_name: str):
    """Decorator to monitor query performance"""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Try to determine row count
                row_count = None
                if hasattr(result, '__len__'):
                    try:
                        row_count = len(result)
                    except:
                        pass
                
                db_optimizer.monitor_query(query_name, duration, row_count)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                db_optimizer.monitor_query(f"{query_name}_error", duration)
                raise
        
        return wrapper
    return decorator