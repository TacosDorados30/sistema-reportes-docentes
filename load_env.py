"""
Cargador de variables de entorno desde archivo .env
"""
import os
from pathlib import Path

def load_env_file():
    """Carga variables de entorno desde archivo .env si existe"""
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        return
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Saltar líneas vacías y comentarios
                if not line or line.startswith('#'):
                    continue
                
                # Procesar líneas con formato KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remover comillas si existen
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Establecer variable de entorno
                    os.environ[key] = value
                # Líneas con formato inválido se ignoran silenciosamente
                pass
        
        # Variables cargadas silenciosamente
        pass
            
    except Exception as e:
        # Errores se ignoran silenciosamente
        pass

if __name__ == "__main__":
    load_env_file()