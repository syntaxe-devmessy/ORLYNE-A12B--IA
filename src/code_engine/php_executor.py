"""
Exécuteur de code PHP
"""

import subprocess
import tempfile
import os
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class PHPExecutor(BaseExecutor):
    """Exécute du code PHP"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code PHP
        
        Args:
            code: Code PHP à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            # Ajout des balises PHP si nécessaire
            if not code.strip().startswith('<?php'):
                code = "<?php\n" + code
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                ['php', temp_file],
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
                "language": "php"
            }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="php"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="php"
            )
    
    def get_docker_image(self) -> str:
        """Image Docker pour PHP"""
        return "php:8.2-cli"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour PHP"""
        return f"php {file_path}"