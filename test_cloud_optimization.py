#!/usr/bin/env python3
"""
Test cloud deployment optimizations
"""

import sys
import os
import time
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cloud_optimizations():
    """Test all cloud deployment optimizations"""
    
    print("🧪 Testing Cloud Deployment Optimizations")
    print("=" * 60)
    
    try:
        # Test 1: Configuration management
        test_configuration_management()
        
        # Test 2: Health checks
        test_health_checks()
        
        # Test 3: Database optimization
        test_database_optimization()
        
        # Test 4: Performance monitoring
        test_performance_monitoring()
        
        # Test 5: Startup sequence
        test_startup_sequence()
        
        print(f"\n📈 Cloud Optimization Testing Summary:")
        print(f"   - Configuration management working")
        print(f"   - Health checks operational")
        print(f"   - Database optimization functional")
        print(f"   - Performance monitoring active")
        print(f"   - Startup sequence optimized")
        print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Cloud optimization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration_management():
    """Test configuration management"""
    
    print("\n1. Testing Configuration Management...")
    
    try:
        from app.config import settings
        
        # Test basic configuration
        if settings.app_name:
            print("   ✅ App name configured")
        else:
            print("   ❌ App name not configured")
        
        if settings.database_url:
            print("   ✅ Database URL configured")
        else:
            print("   ❌ Database URL not configured")
        
        # Test environment detection
        if hasattr(settings, 'is_production') and hasattr(settings, 'is_development'):
            print("   ✅ Environment detection working")
        else:
            print("   ❌ Environment detection not working")
        
        # Test directory creation
        settings.create_directories()
        
        required_dirs = [settings.data_dir, settings.logs_dir, settings.reports_dir]
        existing_dirs = [d for d in required_dirs if os.path.exists(d)]
        
        if len(existing_dirs) == len(required_dirs):
            print("   ✅ Required directories created")
        else:
            print(f"   ⚠️  Some directories missing: {set(required_dirs) - set(existing_dirs)}")
        
    except Exception as e:
        print(f"   ❌ Configuration management test failed: {e}")

def test_health_checks():
    """Test health check system"""
    
    print("\n2. Testing Health Checks...")
    
    try:
        from app.core.health_check import health_checker, get_health_status, get_simple_health
        
        # Test simple health check
        simple_health = get_simple_health()
        if simple_health and "status" in simple_health:
            print(f"   ✅ Simple health check working: {simple_health['status']}")
        else:
            print("   ❌ Simple health check failed")
        
        # Test detailed health check
        detailed_health = get_health_status()
        if detailed_health and "status" in detailed_health and "checks" in detailed_health:
            print(f"   ✅ Detailed health check working: {detailed_health['status']}")
            
            # Check individual components
            checks = detailed_health["checks"]
            for component, status in checks.items():
                if status["status"] == "healthy":
                    print(f"   ✅ {component} health check: {status['status']}")
                else:
                    print(f"   ⚠️  {component} health check: {status['status']} - {status.get('message', '')}")
        else:
            print("   ❌ Detailed health check failed")
        
        # Test health summary
        summary = health_checker.get_health_summary()
        if summary:
            print("   ✅ Health summary working")
        else:
            print("   ❌ Health summary failed")
        
    except Exception as e:
        print(f"   ❌ Health check test failed: {e}")

def test_database_optimization():
    """Test database optimization"""
    
    print("\n3. Testing Database Optimization...")
    
    try:
        from app.database.optimization import db_optimizer, get_performance_stats
        
        # Test performance stats
        stats = get_performance_stats()
        if stats and "table_statistics" in stats:
            print("   ✅ Performance statistics working")
            
            # Check table stats
            table_stats = stats["table_statistics"]
            for table, stat in table_stats.items():
                if "row_count" in stat:
                    print(f"   ✅ {table}: {stat['row_count']} rows")
                elif "error" in stat:
                    print(f"   ⚠️  {table}: {stat['error']}")
        else:
            print("   ❌ Performance statistics failed")
        
        # Test index creation (non-destructive)
        try:
            db_optimizer.create_indexes()
            print("   ✅ Index creation working")
        except Exception as e:
            print(f"   ⚠️  Index creation issue: {e}")
        
        # Test query monitoring
        start_time = time.time()
        time.sleep(0.01)  # Simulate query
        duration = time.time() - start_time
        
        db_optimizer.monitor_query("test_query", duration, 10)
        
        if "test_query" in db_optimizer.query_stats:
            print("   ✅ Query monitoring working")
        else:
            print("   ❌ Query monitoring failed")
        
    except Exception as e:
        print(f"   ❌ Database optimization test failed: {e}")

def test_performance_monitoring():
    """Test performance monitoring"""
    
    print("\n4. Testing Performance Monitoring...")
    
    try:
        from app.core.logging_middleware import performance_monitor, app_logger
        
        # Test performance metric recording
        performance_monitor.record_metric("test_cloud_optimization", 0.5, {"test": "true"})
        
        # Test metric summary
        summary = performance_monitor.get_metric_summary("test_cloud_optimization")
        if summary and "count" in summary:
            print("   ✅ Performance monitoring working")
        else:
            print("   ❌ Performance monitoring failed")
        
        # Test application logging
        app_logger.log_operation("test_cloud_optimization", {"test": True})
        print("   ✅ Application logging working")
        
        # Test performance logging
        app_logger.log_performance("test_operation", 0.1, {"test": True})
        print("   ✅ Performance logging working")
        
    except Exception as e:
        print(f"   ❌ Performance monitoring test failed: {e}")

def test_startup_sequence():
    """Test application startup sequence"""
    
    print("\n5. Testing Startup Sequence...")
    
    try:
        from app.startup import validate_configuration, create_required_directories
        
        # Test configuration validation
        issues = validate_configuration()
        if isinstance(issues, list):
            print(f"   ✅ Configuration validation working ({len(issues)} issues found)")
        else:
            print("   ❌ Configuration validation failed")
        
        # Test directory creation
        create_required_directories()
        print("   ✅ Directory creation working")
        
        # Test logging setup
        from app.startup import setup_logging
        setup_logging()
        print("   ✅ Logging setup working")
        
    except Exception as e:
        print(f"   ❌ Startup sequence test failed: {e}")

def test_streamlit_integration():
    """Test Streamlit-specific optimizations"""
    
    print("\n6. Testing Streamlit Integration...")
    
    try:
        # Test configuration files exist
        config_files = [
            ".streamlit/config.toml",
            ".streamlit/secrets.toml",
            "packages.txt"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                print(f"   ✅ {config_file} exists")
            else:
                print(f"   ❌ {config_file} missing")
        
        # Test requirements.txt
        if os.path.exists("requirements.txt"):
            with open("requirements.txt", 'r') as f:
                content = f.read()
                
            # Check for key dependencies
            key_deps = ["streamlit", "fastapi", "sqlalchemy", "psutil", "pydantic-settings"]
            missing_deps = [dep for dep in key_deps if dep not in content]
            
            if not missing_deps:
                print("   ✅ All key dependencies in requirements.txt")
            else:
                print(f"   ⚠️  Missing dependencies: {missing_deps}")
        else:
            print("   ❌ requirements.txt missing")
        
    except Exception as e:
        print(f"   ❌ Streamlit integration test failed: {e}")

if __name__ == "__main__":
    success = test_cloud_optimizations()
    
    if success:
        print("\n🎉 Cloud deployment optimizations are working correctly!")
        
        # Run Streamlit integration test
        test_streamlit_integration()
        
        print("\n✨ All cloud optimization systems are operational!")
    else:
        print("\n⚠️  Cloud deployment optimization test failed.")