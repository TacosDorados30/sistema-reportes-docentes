"""
Health check endpoints for monitoring
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time

from app.core.health_check import health_checker, get_health_status, get_simple_health
from app.core.logging_middleware import app_logger

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check() -> Dict[str, str]:
    """Simple health check endpoint"""
    
    start_time = time.time()
    
    try:
        result = get_simple_health()
        
        # Log slow health checks
        duration = time.time() - start_time
        if duration > 1.0:
            app_logger.log_operation(
                "slow_health_check",
                {"duration": duration},
                "WARNING"
            )
        
        return result
        
    except Exception as e:
        app_logger.log_operation(
            "health_check_error",
            {"error": str(e)},
            "ERROR"
        )
        raise HTTPException(status_code=503, detail="Health check failed")

@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with all system information"""
    
    start_time = time.time()
    
    try:
        result = get_health_status()
        
        # Log the health check
        health_checker.log_health_check(result)
        
        # Log performance
        duration = time.time() - start_time
        app_logger.log_performance(
            "detailed_health_check",
            duration,
            {"status": result["status"]}
        )
        
        return result
        
    except Exception as e:
        app_logger.log_operation(
            "detailed_health_check_error",
            {"error": str(e)},
            "ERROR"
        )
        raise HTTPException(status_code=503, detail="Detailed health check failed")

@router.get("/summary")
async def health_summary() -> Dict[str, Any]:
    """Health check summary and history"""
    
    try:
        summary = health_checker.get_health_summary()
        return summary
        
    except Exception as e:
        app_logger.log_operation(
            "health_summary_error",
            {"error": str(e)},
            "ERROR"
        )
        raise HTTPException(status_code=503, detail="Health summary failed")

@router.get("/readiness")
async def readiness_check() -> Dict[str, str]:
    """Kubernetes-style readiness probe"""
    
    try:
        health = get_health_status()
        
        # Application is ready if status is healthy or warning
        # Critical status means not ready
        if health["status"] in ["healthy", "warning"]:
            return {"status": "ready", "message": "Application is ready to serve requests"}
        else:
            raise HTTPException(
                status_code=503, 
                detail="Application is not ready"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Readiness check failed: {str(e)}"
        )

@router.get("/liveness")
async def liveness_check() -> Dict[str, str]:
    """Kubernetes-style liveness probe"""
    
    try:
        # Simple check - if we can respond, we're alive
        return {"status": "alive", "message": "Application is running"}
        
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Liveness check failed: {str(e)}"
        )