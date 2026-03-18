"""
Exécuteur de code Ruby
"""

import subprocess
import tempfile
import os
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class RubyExecutor(BaseExecutor):
    """Exécute du code Ruby"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code Ruby
        
        Args:
            code: Code Ruby à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rb', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                ['ruby', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            os.unlink(temp_file)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode,
                "language": "ruby"
            }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="ruby"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="ruby"
            )
    
    def get_docker_image(self) -> str:
        """Image Docker pour Ruby"""
        return "ruby:3.2-slim"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour Ruby"""
        return f"ruby {file_path}"