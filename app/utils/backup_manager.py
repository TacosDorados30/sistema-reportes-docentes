"""
Database backup and recovery utilities
"""

import os
import shutil
import sqlite3
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.config import settings

class BackupManager:
    """Manage database backups and recovery"""
    
    def __init__(self):
        """Initialize backup manager"""
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        self.db_path = settings.database_url.replace("sqlite:///", "")
        if self.db_path.startswith("./"):
            self.db_path = self.db_path[2:]
    
    def create_backup(self, include_data: bool = True) -> Dict[str, Any]:
        """Create a complete backup of the database"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / f"{backup_name}.zip"
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                
                # 1. Backup database file
                if os.path.exists(self.db_path):
                    backup_zip.write(self.db_path, "database.db")
                
                # 2. Backup configuration
                if os.path.exists(".env"):
                    backup_zip.write(".env", "config/.env")
                
                if os.path.exists("requirements.txt"):
                    backup_zip.write("requirements.txt", "config/requirements.txt")
                
                # 3. Export data as JSON for portability
                if include_data:
                    data_export = self._export_data_as_json()
                    backup_zip.writestr("data_export.json", json.dumps(data_export, indent=2, default=str))
                
                # 4. Create backup metadata
                metadata = {
                    "backup_date": datetime.now().isoformat(),
                    "database_path": self.db_path,
                    "include_data": include_data,
                    "app_version": settings.app_version,
                    "environment": settings.environment
                }
                backup_zip.writestr("backup_metadata.json", json.dumps(metadata, indent=2))
            
            backup_size = backup_path.stat().st_size
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "backup_name": backup_name,
                "size_bytes": backup_size,
                "size_mb": round(backup_size / (1024 * 1024), 2),
                "timestamp": timestamp
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _export_data_as_json(self) -> Dict[str, Any]:
        """Export all data as JSON for portability"""
        
        db = SessionLocal()
        try:
            crud = FormularioCRUD(db)
            
            # Get all forms with related data
            all_forms = crud.get_all_formularios(limit=10000)
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "total_forms": len(all_forms),
                "forms": []
            }
            
            for form in all_forms:
                form_data = {
                    "id": form.id,
                    "nombre_completo": form.nombre_completo,
                    "correo_institucional": form.correo_institucional,
                    "año_academico": getattr(form, 'año_academico', None),
                    "trimestre": getattr(form, 'trimestre', None),
                    "estado": form.estado.value,
                    "fecha_envio": form.fecha_envio.isoformat() if form.fecha_envio else None,
                    "fecha_revision": form.fecha_revision.isoformat() if form.fecha_revision else None,
                    "revisado_por": form.revisado_por,
                    "cursos_capacitacion": [],
                    "publicaciones": [],
                    "eventos_academicos": [],
                    "diseno_curricular": [],
                    "movilidad": [],
                    "reconocimientos": [],
                    "certificaciones": []
                }
                
                # Safely extract related data
                try:
                    if hasattr(form, 'cursos_capacitacion') and form.cursos_capacitacion:
                        for curso in form.cursos_capacitacion:
                            form_data["cursos_capacitacion"].append({
                                "nombre_curso": curso.nombre_curso,
                                "fecha": curso.fecha.isoformat() if curso.fecha else None,
                                "horas": curso.horas
                            })
                except:
                    pass
                
                # Extract publicaciones
                try:
                    if hasattr(form, 'publicaciones') and form.publicaciones:
                        for pub in form.publicaciones:
                            form_data["publicaciones"].append({
                                "autores": pub.autores,
                                "titulo": pub.titulo,
                                "evento_revista": pub.evento_revista,
                                "estatus": pub.estatus.value if hasattr(pub.estatus, 'value') else str(pub.estatus)
                            })
                except:
                    pass
                
                # Extract eventos academicos
                try:
                    if hasattr(form, 'eventos_academicos') and form.eventos_academicos:
                        for evento in form.eventos_academicos:
                            form_data["eventos_academicos"].append({
                                "nombre_evento": evento.nombre_evento,
                                "fecha": evento.fecha.isoformat() if evento.fecha else None,
                                "tipo_participacion": evento.tipo_participacion.value if hasattr(evento.tipo_participacion, 'value') else str(evento.tipo_participacion)
                            })
                except:
                    pass
                
                # Extract diseño curricular
                try:
                    if hasattr(form, 'diseno_curricular') and form.diseno_curricular:
                        for diseno in form.diseno_curricular:
                            form_data["diseno_curricular"].append({
                                "nombre_curso": diseno.nombre_curso,
                                "descripcion": getattr(diseno, 'descripcion', '')
                            })
                except:
                    pass
                
                # Extract movilidad
                try:
                    if hasattr(form, 'movilidad') and form.movilidad:
                        for mov in form.movilidad:
                            form_data["movilidad"].append({
                                "descripcion": mov.descripcion,
                                "tipo": mov.tipo.value if hasattr(mov.tipo, 'value') else str(mov.tipo),
                                "fecha": mov.fecha.isoformat() if mov.fecha else None
                            })
                except:
                    pass
                
                # Extract reconocimientos
                try:
                    if hasattr(form, 'reconocimientos') and form.reconocimientos:
                        for rec in form.reconocimientos:
                            form_data["reconocimientos"].append({
                                "nombre": rec.nombre,
                                "tipo": rec.tipo.value if hasattr(rec.tipo, 'value') else str(rec.tipo),
                                "fecha": rec.fecha.isoformat() if rec.fecha else None
                            })
                except:
                    pass
                
                # Extract certificaciones
                try:
                    if hasattr(form, 'certificaciones') and form.certificaciones:
                        for cert in form.certificaciones:
                            form_data["certificaciones"].append({
                                "nombre": cert.nombre,
                                "fecha_obtencion": cert.fecha_obtencion.isoformat() if cert.fecha_obtencion else None,
                                "fecha_vencimiento": cert.fecha_vencimiento.isoformat() if cert.fecha_vencimiento else None,
                                "vigente": getattr(cert, 'vigente', True)
                            })
                except:
                    pass
                
                export_data["forms"].append(form_data)
            
            return export_data
            
        finally:
            db.close()
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        
        backups = []
        
        for backup_file in self.backup_dir.glob("backup_*.zip"):
            try:
                stat = backup_file.stat()
                
                # Extract timestamp from filename
                timestamp_str = backup_file.stem.replace("backup_", "")
                
                backups.append({
                    "name": backup_file.name,
                    "path": str(backup_file),
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(stat.st_ctime),
                    "timestamp": timestamp_str
                })
                
            except Exception as e:
                print(f"Error reading backup {backup_file}: {e}")
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return backups
    
    def restore_backup(self, backup_path: str) -> Dict[str, Any]:
        """Restore database from backup"""
        
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return {"success": False, "error": "Backup file not found"}
        
        try:
            # Create restore directory
            restore_dir = Path("temp_restore")
            restore_dir.mkdir(exist_ok=True)
            
            # Extract backup
            with zipfile.ZipFile(backup_file, 'r') as backup_zip:
                backup_zip.extractall(restore_dir)
            
            # Read metadata
            metadata_path = restore_dir / "backup_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            # Backup current database
            current_backup = self.create_backup(include_data=True)
            
            # Restore database file
            restored_db_path = restore_dir / "database.db"
            if restored_db_path.exists():
                # Stop any active connections
                # Copy restored database
                shutil.copy2(restored_db_path, self.db_path)
            
            # Clean up
            shutil.rmtree(restore_dir)
            
            return {
                "success": True,
                "metadata": metadata,
                "current_backup": current_backup.get("backup_name") if current_backup.get("success") else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_backup(self, backup_name: str) -> bool:
        """Delete a backup file"""
        
        try:
            backup_path = self.backup_dir / backup_name
            if backup_path.exists():
                backup_path.unlink()
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting backup {backup_name}: {e}")
            return False
    
    def get_backup_info(self, backup_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a backup file"""
        
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return None
        
        try:
            info = {
                "name": backup_file.name,
                "size_mb": round(backup_file.stat().st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(backup_file.stat().st_ctime),
                "metadata": None
            }
            
            # Try to read metadata from backup
            with zipfile.ZipFile(backup_file, 'r') as backup_zip:
                if "backup_metadata.json" in backup_zip.namelist():
                    metadata_content = backup_zip.read("backup_metadata.json")
                    info["metadata"] = json.loads(metadata_content)
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def import_data_from_json(self, json_file_path: str) -> Dict[str, Any]:
        """Import data from JSON backup file"""
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            db = SessionLocal()
            try:
                crud = FormularioCRUD(db)
                imported_count = 0
                errors = []
                
                for form_data in data.get("forms", []):
                    try:
                        # Create form entry
                        form_dict = {
                            "nombre_completo": form_data["nombre_completo"],
                            "correo_institucional": form_data["correo_institucional"],
                            "año_academico": form_data.get("año_academico"),
                            "trimestre": form_data.get("trimestre"),
                            "estado": form_data.get("estado", "PENDIENTE"),
                            "fecha_envio": datetime.fromisoformat(form_data["fecha_envio"]) if form_data.get("fecha_envio") else datetime.now(),
                            "fecha_revision": datetime.fromisoformat(form_data["fecha_revision"]) if form_data.get("fecha_revision") else None,
                            "revisado_por": form_data.get("revisado_por")
                        }
                        
                        # Add related data
                        form_dict["cursos_capacitacion"] = form_data.get("cursos_capacitacion", [])
                        form_dict["publicaciones"] = form_data.get("publicaciones", [])
                        form_dict["eventos_academicos"] = form_data.get("eventos_academicos", [])
                        form_dict["diseno_curricular"] = form_data.get("diseno_curricular", [])
                        form_dict["movilidad"] = form_data.get("movilidad", [])
                        form_dict["reconocimientos"] = form_data.get("reconocimientos", [])
                        form_dict["certificaciones"] = form_data.get("certificaciones", [])
                        
                        # Create form using CRUD
                        created_form = crud.create_formulario_completo(form_dict)
                        if created_form:
                            imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Error importing form {form_data.get('id', 'unknown')}: {str(e)}")
                
                db.commit()
                
                return {
                    "success": True,
                    "imported_count": imported_count,
                    "total_forms": len(data.get("forms", [])),
                    "errors": errors
                }
                
            finally:
                db.close()
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Keep only the most recent backups"""
        
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        deleted_count = 0
        backups_to_delete = backups[keep_count:]
        
        for backup in backups_to_delete:
            if self.delete_backup(backup["name"]):
                deleted_count += 1
        
        return deleted_count
    
    def verify_backup_integrity(self, backup_path: str) -> Dict[str, Any]:
        """Verify backup file integrity"""
        
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return {"success": False, "error": "Backup file not found"}
        
        try:
            verification = {
                "success": True,
                "file_exists": True,
                "file_size": backup_file.stat().st_size,
                "can_extract": False,
                "has_database": False,
                "has_metadata": False,
                "has_data_export": False,
                "errors": []
            }
            
            # Try to open and read the zip file
            with zipfile.ZipFile(backup_file, 'r') as backup_zip:
                verification["can_extract"] = True
                
                file_list = backup_zip.namelist()
                
                # Check for required files
                if "database.db" in file_list:
                    verification["has_database"] = True
                
                if "backup_metadata.json" in file_list:
                    verification["has_metadata"] = True
                    
                    # Try to read metadata
                    try:
                        metadata_content = backup_zip.read("backup_metadata.json")
                        metadata = json.loads(metadata_content)
                        verification["metadata"] = metadata
                    except Exception as e:
                        verification["errors"].append(f"Error reading metadata: {str(e)}")
                
                if "data_export.json" in file_list:
                    verification["has_data_export"] = True
                    
                    # Try to read data export
                    try:
                        data_content = backup_zip.read("data_export.json")
                        data = json.loads(data_content)
                        verification["data_export_info"] = {
                            "total_forms": data.get("total_forms", 0),
                            "export_date": data.get("export_date")
                        }
                    except Exception as e:
                        verification["errors"].append(f"Error reading data export: {str(e)}")
            
            return verification
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Global backup manager instance
backup_manager = BackupManager()