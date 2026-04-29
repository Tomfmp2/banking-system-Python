import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any
from utils.exceptions import DataCorruptionError

class JsonHandler:
    """
    Manejador de persistencia JSON con soporte para bloqueo de archivos (file locking)
    y validación de integridad.
    """
    def __init__(self, file_path: str, default_structure: Dict[str, Any]):
        self.file_path = file_path
        self.lock_file = f"{file_path}.lock"
        self.default_structure = default_structure
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Crea el archivo con la estructura por defecto si no existe."""
        if not os.path.exists(self.file_path):
            # Asegurarse de que el directorio existe
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            self._write_raw(self.default_structure)

    def _acquire_lock(self, timeout: int = 5) -> None:
        """Adquiere un bloqueo sobre el archivo usando un archivo de bloqueo."""
        start_time = time.time()
        while True:
            try:
                # O_CREAT | O_EXCL asegura que la operación sea atómica y falle si el archivo ya existe
                fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.close(fd)
                break
            except FileExistsError:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"No se pudo adquirir el bloqueo para {self.file_path}")
                time.sleep(0.1)

    def _release_lock(self) -> None:
        """Libera el bloqueo del archivo."""
        try:
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except OSError:
            pass

    def _write_raw(self, data: Dict[str, Any]) -> None:
        """Escribe datos crudos al archivo JSON de forma atómica."""
        self._acquire_lock()
        try:
            # Escribir primero en un archivo temporal
            temp_file = f"{self.file_path}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            # Reemplazar el archivo original (operación atómica en POSIX, segura en Windows con replace)
            os.replace(temp_file, self.file_path)
        except Exception as e:
            raise DataCorruptionError(f"Error al escribir en {self.file_path}: {str(e)}")
        finally:
            self._release_lock()

    def read(self) -> Dict[str, Any]:
        """Lee y valida los datos del archivo JSON."""
        self._acquire_lock()
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError:
            raise DataCorruptionError(f"El archivo {self.file_path} contiene JSON inválido.")
        except Exception as e:
            raise DataCorruptionError(f"Error al leer {self.file_path}: {str(e)}")
        finally:
            self._release_lock()

    def write(self, main_key: str, data_list: List[Dict[str, Any]]) -> None:
        """
        Escribe la lista de datos actualizando los metadatos.
        `main_key` es la clave principal ('accounts' o 'transactions').
        """
        data_to_write = {
            main_key: data_list,
            "metadata": {
                f"total_{main_key}": len(data_list),
                "last_updated": datetime.now().isoformat()
            }
        }
        self._write_raw(data_to_write)
