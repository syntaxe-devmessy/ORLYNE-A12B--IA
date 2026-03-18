"""
Exécuteur de code Python
"""

import subprocess
import tempfile
import os
import sys
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class PythonExecutor(BaseExecutor):
    """Exécute du code Python"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code Python
        
        Args:
            code: Code Python à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            # Création d'un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Exécution dans un sous-processus
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, "PYTHONPATH": ""}  # Isolation
            )
            
            # Nettoyage
            os.unlink(temp_file)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode,
                "language": "python"
            }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="python"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="python"
            )
    
    def get_docker_image(self) -> str:
        """Image Docker pour Python"""
        return "python:3.11-slim"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour Python"""
        return f"python {file_path}"