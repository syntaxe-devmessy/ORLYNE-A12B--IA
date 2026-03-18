"""
Exécuteur de code JavaScript
"""

import subprocess
import tempfile
import os
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class JavaScriptExecutor(BaseExecutor):
    """Exécute du code JavaScript avec Node.js"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code JavaScript
        
        Args:
            code: Code JavaScript à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            # Vérification de Node.js
            if not self._check_node_installed():
                return self._execute_with_docker(code, timeout)
            
            # Création d'un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Exécution
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Nettoyage
            os.unlink(temp_file)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode,
                "language": "javascript"
            }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="javascript"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="javascript"
            )
    
    def _check_node_installed(self) -> bool:
        """Vérifie si Node.js est installé"""
        try:
            subprocess.run(['node', '--version'], capture_output=True)
            return True
        except FileNotFoundError:
            return False
    
    def get_docker_image(self) -> str:
        """Image Docker pour Node.js"""
        return "node:18-slim"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour Node.js"""
        return f"node {file_path}"