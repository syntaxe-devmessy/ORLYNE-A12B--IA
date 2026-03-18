"""
Exécuteur de code Go
"""

import subprocess
import tempfile
import os
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class GoExecutor(BaseExecutor):
    """Exécute du code Go"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code Go
        
        Args:
            code: Code Go à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Fichier source
                go_file = os.path.join(temp_dir, "main.go")
                with open(go_file, 'w') as f:
                    f.write(code)
                
                # Exécution directe avec go run
                result = subprocess.run(
                    ['go', 'run', go_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env={**os.environ, "GOPATH": os.path.join(temp_dir, "go")}
                )
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "exit_code": result.returncode,
                    "language": "go"
                }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="go"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="go"
            )
    
    def get_docker_image(self) -> str:
        """Image Docker pour Go"""
        return "golang:1.20-slim"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour Go"""
        return f"go run {file_path}"