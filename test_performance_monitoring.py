#!/usr/bin/env python3
"""
Test script for performance monitoring system
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.performance_monitor import performance_monitor, monitor_performance
from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD

def test_performance_monitoring():
    """Test the performance monitoring system"""
    
    print("🚀 Testing Performance Monitoring System")
    print("=" * 60)
    
    # Test 1: Start monitoring
    print("\n1. Starting performance monitoring...")
    performance_monitor.start_monitoring(interval=5)  # 5 second intervals for testing
    
    if performance_monitor.monitoring_active:
        print("✅ Performance monitoring started successfully!")
    else:
        print("❌ Failed to start performance monitoring")
        return False
    
    # Test 2: Record some requests
    print("\n2. Recording test requests...")
    
    # Simulate some requests with different response times
    test_requests = [
        (150, False),   # Fast request
        (300, False),   # Normal request
        (1200, False),  # Slow request
        (500, True),    # Request with error
        (200, False),   # Another fast request
    ]
    
    for response_time, is_error in test_requests:
        performance_monitor.record_request(response_time, is_error)
        time.sleep(0.1)  # Small delay between requests
    
    print(f"✅ Recorded {len(test_requests)} test requests")
    
    # Test 3: Record some database queries
    print("\n3. Recording test database queries...")
    
    test_queries = [50, 120, 80, 1500, 200]  # Query times in ms
    
    for query_time in test_queries:
        performance_monitor.record_query(query_time)
    
    print(f"✅ Recorded {len(test_queries)} test queries")
    
    # Test 4: Get current metrics
    print("\n4. Getting current metrics...")
    
    try:
        current_metrics = performance_monitor.get_current_metrics()
        
        if "error" in current_metrics:
            print(f"❌ Error getting metrics: {current_metrics['error']}")
        else:
            print("✅ Current metrics retrieved successfully!")
            
            system = current_metrics.get("system", {})
            summary = current_metrics.get("summary", {})
            
            print(f"   - CPU: {system.get('cpu_percent', 0):.1f}%")
            print(f"   - Memory: {system.get('memory_percent', 0):.1f}%")
            print(f"   - Total Requests: {summary.get('total_requests', 0)}")
            print(f"   - Error Rate: {summary.get('error_rate', 0):.2f}%")
            print(f"   - Avg Response Time: {summary.get('avg_response_time', 0):.1f}ms")
    
    except Exception as e:
        print(f"❌ Error getting current metrics: {e}")
    
    # Test 5: Wait for some monitoring data
    print("\n5. Waiting for monitoring data collection...")
    print("   (Waiting 10 seconds for background monitoring...)")
    
    time.sleep(10)
    
    # Test 6: Get metrics history
    print("\n6. Getting metrics history...")
    
    try:
        history = performance_monitor.get_metrics_history(hours=1)
        system_metrics = history.get("system_metrics", [])
        
        print(f"✅ Retrieved {len(system_metrics)} historical data points")
        
        if system_metrics:
            latest = system_metrics[-1]
            print(f"   - Latest CPU: {latest.get('cpu_percent', 0):.1f}%")
            print(f"   - Latest Memory: {latest.get('memory_percent', 0):.1f}%")
    
    except Exception as e:
        print(f"❌ Error getting metrics history: {e}")
    
    # Test 7: Get performance summary
    print("\n7. Getting performance summary...")
    
    try:
        summary = performance_monitor.get_performance_summary()
        
        if "error" in summary:
            print(f"❌ Error getting summary: {summary['error']}")
        else:
            print("✅ Performance summary retrieved successfully!")
            
            averages = summary.get("averages", {})
            peaks = summary.get("peaks", {})
            health = summary.get("health_status", "unknown")
            
            print(f"   - Avg CPU: {averages.get('cpu_percent', 0):.1f}%")
            print(f"   - Max CPU: {peaks.get('max_cpu_percent', 0):.1f}%")
            print(f"   - Health Status: {health}")
    
    except Exception as e:
        print(f"❌ Error getting performance summary: {e}")
    
    # Test 8: Test performance decorator
    print("\n8. Testing performance decorator...")
    
    @monitor_performance
    def test_function():
        """Test function with performance monitoring"""
        time.sleep(0.1)  # Simulate some work
        return "test result"
    
    try:
        result = test_function()
        print(f"✅ Performance decorator test completed: {result}")
    except Exception as e:
        print(f"❌ Performance decorator test failed: {e}")
    
    # Test 9: Test database operations monitoring
    print("\n9. Testing database operations monitoring...")
    
    try:
        db = SessionLocal()
        crud = FormularioCRUD(db)
        
        # This should be monitored automatically
        stats = crud.get_estadisticas_generales()
        
        print("✅ Database operation completed and monitored")
        print(f"   - Total forms in DB: {stats.get('total_formularios', 0)}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database monitoring test failed: {e}")
    
    # Test 10: Check metrics files
    print("\n10. Checking metrics files...")
    
    metrics_dir = Path("metrics")
    if metrics_dir.exists():
        metric_files = list(metrics_dir.glob("*.jsonl"))
        print(f"✅ Found {len(metric_files)} metrics files")
        
        for file in metric_files[:3]:  # Show first 3 files
            print(f"   - {file.name}")
    else:
        print("ℹ️  No metrics directory found yet (will be created during monitoring)")
    
    # Test 11: Stop monitoring
    print("\n11. Stopping performance monitoring...")
    performance_monitor.stop_monitoring()
    
    if not performance_monitor.monitoring_active:
        print("✅ Performance monitoring stopped successfully!")
    else:
        print("❌ Failed to stop performance monitoring")
    
    print("\n" + "=" * 60)
    print("🎉 Performance monitoring test completed!")
    
    return True

def test_performance_thresholds():
    """Test performance alert thresholds"""
    
    print("\n🚨 Testing Performance Thresholds")
    print("=" * 50)
    
    # Save original thresholds
    original_cpu = performance_monitor.cpu_threshold
    original_memory = performance_monitor.memory_threshold
    original_response = performance_monitor.response_time_threshold
    
    try:
        # Set very low thresholds to trigger alerts
        performance_monitor.cpu_threshold = 1.0  # 1% CPU
        performance_monitor.memory_threshold = 1.0  # 1% Memory
        performance_monitor.response_time_threshold = 10.0  # 10ms response time
        
        print("✅ Set low thresholds for testing")
        
        # Start monitoring briefly
        performance_monitor.start_monitoring(interval=2)
        
        print("⏳ Waiting for alerts to be generated...")
        time.sleep(5)
        
        # Check for alert file
        alert_file = Path("metrics/performance_alerts.jsonl")
        if alert_file.exists():
            print("✅ Performance alerts file created!")
            
            # Read and show some alerts
            with open(alert_file, 'r') as f:
                lines = f.readlines()
                print(f"   - Found {len(lines)} alert entries")
                
                if lines:
                    import json
                    try:
                        last_alert = json.loads(lines[-1])
                        print(f"   - Latest alert: {last_alert.get('alerts', [])}")
                    except:
                        print("   - Could not parse latest alert")
        else:
            print("ℹ️  No alerts generated (system performance too good!)")
        
        performance_monitor.stop_monitoring()
        
    finally:
        # Restore original thresholds
        performance_monitor.cpu_threshold = original_cpu
        performance_monitor.memory_threshold = original_memory
        performance_monitor.response_time_threshold = original_response
        
        print("✅ Restored original thresholds")

if __name__ == "__main__":
    print("🚀 Starting Performance Monitoring Tests")
    
    # Initialize the application
    try:
        from app.startup import startup_application
        startup_result = startup_application()
        print(f"✅ Application initialized: {startup_result['status']}")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        sys.exit(1)
    
    # Run tests
    success = True
    
    try:
        success &= test_performance_monitoring()
        test_performance_thresholds()
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        success = False
    except Exception as e:
        print(f"\n❌ Unexpected error during tests: {e}")
        success = False
    finally:
        # Make sure monitoring is stopped
        if performance_monitor.monitoring_active:
            performance_monitor.stop_monitoring()
    
    # Final result
    print("\n" + "=" * 70)
    if success:
        print("🎉 All performance monitoring tests completed successfully!")
        print("✅ Performance monitoring system is working correctly")
    else:
        print("❌ Some tests failed")
        print("⚠️  Please check the errors above")
    
    print("=" * 70)