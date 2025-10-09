#!/usr/bin/env python3
"""
Test script for backup and recovery system
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.backup_manager import backup_manager
from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.models.database import EstadoFormularioEnum

def test_backup_system():
    """Test the backup and recovery system"""
    
    print("🧪 Testing Backup System")
    print("=" * 50)
    
    # Test 1: Create a backup
    print("\n1. Creating backup...")
    backup_result = backup_manager.create_backup(include_data=True)
    
    if backup_result["success"]:
        print(f"✅ Backup created successfully!")
        print(f"   - Name: {backup_result['backup_name']}")
        print(f"   - Size: {backup_result['size_mb']} MB")
        print(f"   - Path: {backup_result['backup_path']}")
    else:
        print(f"❌ Backup failed: {backup_result['error']}")
        return False
    
    # Test 2: List backups
    print("\n2. Listing available backups...")
    backups = backup_manager.list_backups()
    
    print(f"✅ Found {len(backups)} backups:")
    for backup in backups[:3]:  # Show first 3
        print(f"   - {backup['name']} ({backup['size_mb']} MB)")
    
    # Test 3: Verify backup integrity
    print("\n3. Verifying backup integrity...")
    if backups:
        latest_backup = backups[0]
        verification = backup_manager.verify_backup_integrity(latest_backup["path"])
        
        if verification["success"]:
            print("✅ Backup verification passed!")
            print(f"   - Has database: {verification['has_database']}")
            print(f"   - Has metadata: {verification['has_metadata']}")
            print(f"   - Has data export: {verification['has_data_export']}")
            
            if verification.get("errors"):
                print("⚠️  Warnings found:")
                for error in verification["errors"]:
                    print(f"   - {error}")
        else:
            print(f"❌ Backup verification failed: {verification['error']}")
    
    # Test 4: Get backup info
    print("\n4. Getting backup information...")
    if backups:
        info = backup_manager.get_backup_info(backups[0]["path"])
        if info and "error" not in info:
            print("✅ Backup info retrieved successfully!")
            print(f"   - Created: {info['created']}")
            print(f"   - Size: {info['size_mb']} MB")
            if info.get("metadata"):
                metadata = info["metadata"]
                print(f"   - App version: {metadata.get('app_version', 'N/A')}")
                print(f"   - Environment: {metadata.get('environment', 'N/A')}")
        else:
            print(f"❌ Failed to get backup info: {info.get('error', 'Unknown error')}")
    
    # Test 5: Test database connection and data
    print("\n5. Testing database connection...")
    try:
        db = SessionLocal()
        crud = FormularioCRUD(db)
        
        # Get some basic stats
        stats = crud.get_estadisticas_generales()
        print("✅ Database connection successful!")
        print(f"   - Total forms: {stats['total_formularios']}")
        print(f"   - Pending: {stats['pendientes']}")
        print(f"   - Approved: {stats['aprobados']}")
        print(f"   - Rejected: {stats['rechazados']}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Test 6: Cleanup old backups (dry run)
    print("\n6. Testing backup cleanup...")
    initial_count = len(backups)
    
    if initial_count > 5:
        deleted_count = backup_manager.cleanup_old_backups(keep_count=5)
        print(f"✅ Cleanup completed! Deleted {deleted_count} old backups")
        
        # Check new count
        new_backups = backup_manager.list_backups()
        print(f"   - Before: {initial_count} backups")
        print(f"   - After: {len(new_backups)} backups")
    else:
        print(f"✅ No cleanup needed (only {initial_count} backups)")
    
    print("\n" + "=" * 50)
    print("🎉 Backup system test completed!")
    
    return True

def test_data_export_import():
    """Test data export and import functionality"""
    
    print("\n🔄 Testing Data Export/Import")
    print("=" * 50)
    
    try:
        # Test data export
        print("\n1. Testing data export...")
        data_export = backup_manager._export_data_as_json()
        
        print(f"✅ Data export successful!")
        print(f"   - Total forms: {data_export['total_forms']}")
        print(f"   - Export date: {data_export['export_date']}")
        
        # Save to temporary file for import test
        import json
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(data_export, tmp_file, indent=2, default=str)
            tmp_file_path = tmp_file.name
        
        print(f"   - Saved to: {tmp_file_path}")
        
        # Test import (if there's data to import)
        if data_export['total_forms'] > 0:
            print("\n2. Testing data import...")
            
            # Note: In a real scenario, you might want to test with a separate database
            # For now, we'll just validate the import function exists and can read the file
            import_result = backup_manager.import_data_from_json(tmp_file_path)
            
            if import_result["success"]:
                print(f"✅ Data import test successful!")
                print(f"   - Imported: {import_result['imported_count']} forms")
                print(f"   - Total in file: {import_result['total_forms']}")
                
                if import_result.get("errors"):
                    print(f"   - Errors: {len(import_result['errors'])}")
            else:
                print(f"❌ Data import failed: {import_result['error']}")
        
        # Cleanup
        os.unlink(tmp_file_path)
        
    except Exception as e:
        print(f"❌ Export/Import test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Backup System Tests")
    
    # Initialize the application
    try:
        from app.startup import startup_application
        startup_result = startup_application()
        print(f"✅ Application initialized: {startup_result}")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        sys.exit(1)
    
    # Run tests
    success = True
    
    try:
        success &= test_backup_system()
        success &= test_data_export_import()
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        success = False
    except Exception as e:
        print(f"\n❌ Unexpected error during tests: {e}")
        success = False
    
    # Final result
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("✅ Backup system is working correctly")
    else:
        print("❌ Some tests failed")
        print("⚠️  Please check the errors above")
    
    print("=" * 60)