"""
Exécuteur de code Swift
"""

import subprocess
import tempfile
import os
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class SwiftExecutor(BaseExecutor):
    """Exécute du code Swift"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code Swift
        
        Args:
            code: Code Swift à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Compilation et exécution
            result = subprocess.run(
                ['swift', temp_file],
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
                "language": "swift"
            }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="swift"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="swift"
            )
    
    def get_docker_image(self) -> str:
        """Image Docker pour Swift"""
        return "swift:5.8-slim"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour Swift"""
        return f"swift {file_path}"