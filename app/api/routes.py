from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, List
from datetime import datetime
import logging

# Import database and models
from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.models.schemas import FormData
from sqlalchemy.orm import Session

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["formularios"])

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {"message": "API is working", "status": "ok"}

@router.post("/formulario/enviar")
async def enviar_formulario(form_data: Dict[Any, Any], db: Session = Depends(get_db)):
    """Submit a new form with comprehensive validation and database storage"""
    try:
        logger.info(f"Received form submission from: {form_data.get('correo_institucional')}")
        
        # Validate required fields
        validation_errors = validate_form_data(form_data)
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Errores de validación encontrados",
                    "errors": validation_errors
                }
            )
        
        # Process and clean form data
        processed_data = process_form_data(form_data)
        
        # Create FormData object
        try:
            form_schema = FormData(**processed_data)
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error en la estructura de datos: {str(e)}"
            )
        
        # Save to database
        crud = FormularioCRUD(db)
        
        # Check for duplicate email
        existing_form = crud.get_formulario_by_email(form_schema.correo_institucional)
        if existing_form:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un formulario con este correo electrónico"
            )
        
        # Create new form
        db_form = crud.create_formulario(form_schema)
        
        logger.info(f"Form created successfully with ID: {db_form.id}")
        
        return {
            "success": True,
            "message": "Formulario enviado exitosamente. Será revisado por la administradora.",
            "formulario_id": db_form.id,
            "fecha_envio": db_form.fecha_envio.isoformat() if db_form.fecha_envio else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor. Por favor, intente nuevamente."
        )

@router.get("/admin/metricas")
async def get_metricas_generales():
    """Get general metrics for dashboard"""
    return {
        "total_formularios": 1,
        "formularios_pendientes": 0,
        "formularios_aprobados": 1,
        "formularios_rechazados": 0,
        "total_cursos": 2,
        "total_horas_capacitacion": 60,
        "total_publicaciones": 1,
        "total_eventos": 1,
        "total_disenos_curriculares": 1,
        "total_movilidades": 1,
        "total_reconocimientos": 1,
        "total_certificaciones": 1
    }

def validate_form_data(form_data: Dict[Any, Any]) -> List[str]:
    """Validate form data and return list of errors"""
    errors = []
    
    # Required fields validation
    required_fields = {
        "nombre_completo": "Nombre completo",
        "correo_institucional": "Correo electrónico institucional"
    }
    
    for field, label in required_fields.items():
        value = form_data.get(field)
        if not value or not str(value).strip():
            errors.append(f"{label} es requerido")
    
    # Email format validation
    email = form_data.get("correo_institucional", "").strip()
    if email:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append("El formato del correo electrónico no es válido")
    
    # Validate array fields
    array_fields = [
        "cursos_capacitacion", "publicaciones", "eventos_academicos",
        "diseno_curricular", "movilidad", "reconocimientos", "certificaciones"
    ]
    
    for field in array_fields:
        if field in form_data and form_data[field]:
            field_errors = validate_array_field(form_data[field], field)
            errors.extend(field_errors)
    
    return errors

def validate_array_field(field_data: List[Dict], field_name: str) -> List[str]:
    """Validate array field data"""
    errors = []
    
    if not isinstance(field_data, list):
        errors.append(f"El campo {field_name} debe ser una lista")
        return errors
    
    for i, item in enumerate(field_data):
        if not isinstance(item, dict):
            errors.append(f"Item {i+1} en {field_name} debe ser un objeto")
            continue
        
        # Field-specific validations
        if field_name == "cursos_capacitacion":
            if not item.get("nombre_curso", "").strip():
                errors.append(f"Nombre del curso es requerido en item {i+1}")
            if item.get("horas") and (not str(item["horas"]).isdigit() or int(item["horas"]) <= 0):
                errors.append(f"Número de horas debe ser un número positivo en item {i+1}")
        
        elif field_name == "publicaciones":
            required_pub_fields = ["autores", "titulo", "evento_revista"]
            for req_field in required_pub_fields:
                if not item.get(req_field, "").strip():
                    errors.append(f"{req_field.replace('_', ' ').title()} es requerido en publicación {i+1}")
        
        elif field_name == "eventos_academicos":
            if not item.get("nombre_evento", "").strip():
                errors.append(f"Nombre del evento es requerido en item {i+1}")
        
        # Date validation for fields that have dates
        date_fields = ["fecha", "fecha_obtencion", "fecha_vencimiento"]
        for date_field in date_fields:
            if item.get(date_field):
                try:
                    from datetime import datetime
                    datetime.fromisoformat(item[date_field])
                except ValueError:
                    errors.append(f"Formato de fecha inválido en {date_field} del item {i+1}")
    
    return errors

def process_form_data(form_data: Dict[Any, Any]) -> Dict[Any, Any]:
    """Process and clean form data"""
    processed = {}
    
    # Copy basic fields
    basic_fields = ["nombre_completo", "correo_institucional"]
    for field in basic_fields:
        if field in form_data:
            processed[field] = str(form_data[field]).strip()
    
    # Process array fields
    array_fields = [
        "cursos_capacitacion", "publicaciones", "eventos_academicos",
        "diseno_curricular", "movilidad", "reconocimientos", "certificaciones"
    ]
    
    for field in array_fields:
        if field in form_data and form_data[field]:
            processed[field] = process_array_field(form_data[field], field)
        else:
            processed[field] = []
    
    return processed

def process_array_field(field_data: List[Dict], field_name: str) -> List[Dict]:
    """Process array field data"""
    processed_items = []
    
    for item in field_data:
        if not isinstance(item, dict):
            continue
        
        processed_item = {}
        
        # Process each field in the item
        for key, value in item.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            
            # Clean string values
            if isinstance(value, str):
                processed_item[key] = value.strip()
            # Convert numeric strings to integers for specific fields
            elif key in ["horas"]:
                if isinstance(value, str) and value.isdigit():
                    processed_item[key] = int(value)
                elif isinstance(value, (int, float)):
                    processed_item[key] = int(value)
            # Handle boolean fields
            elif key in ["vigente"] and isinstance(value, str):
                processed_item[key] = value.lower() in ['true', '1', 'yes', 'si']
            else:
                processed_item[key] = value
        
        # Only add items that have meaningful data
        if processed_item:
            processed_items.append(processed_item)
    
    return processed_items

@router.get("/formulario/status/{formulario_id}")
async def get_formulario_status(formulario_id: int, db: Session = Depends(get_db)):
    """Get status of a submitted form"""
    try:
        crud = FormularioCRUD(db)
        formulario = crud.get_formulario(formulario_id)
        
        if not formulario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Formulario no encontrado"
            )
        
        return {
            "formulario_id": formulario.id,
            "estado": formulario.estado.value,
            "fecha_envio": formulario.fecha_envio.isoformat() if formulario.fecha_envio else None,
            "fecha_revision": formulario.fecha_revision.isoformat() if formulario.fecha_revision else None,
            "revisado_por": formulario.revisado_por,
            "comentarios": getattr(formulario, 'comentarios', None)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting form status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el estado del formulario"
        )