from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

router = APIRouter(tags=["formularios"])

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {"message": "API is working", "status": "ok"}

@router.post("/formulario/enviar")
async def enviar_formulario(form_data: Dict[Any, Any]):
    """Submit a new form - simplified version"""
    try:
        # Basic validation
        if not form_data.get("nombre_completo"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre completo es requerido"
            )
        
        if not form_data.get("correo_institucional"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correo institucional es requerido"
            )
        
        # For now, simulate successful submission
        return {
            "success": True,
            "message": "Formulario enviado exitosamente. Será revisado por la administradora.",
            "formulario_id": 1
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el formulario: {str(e)}"
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