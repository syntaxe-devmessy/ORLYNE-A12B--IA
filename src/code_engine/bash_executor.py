"""
Exécuteur de scripts Bash
"""

import subprocess
import tempfile
import os
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class BashExecutor(BaseExecutor):
    """Exécute des scripts Bash"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute un script Bash
        
        Args:
            code: Script Bash à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            # Ajout du shebang si nécessaire
            if not code.startswith('#!'):
                code = '#!/bin/bash\n' + code
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Rendre le script exécutable
            os.chmod(temp_file, 0o755)
            
            # Exécution
            result = subprocess.run(
                ['/bin/bash', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                env={}  # Environnement vide pour isolation
            )
            
            os.unlink(temp_file)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode,
                "language": "bash"
            }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="bash"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="bash"
            )
    
    def get_docker_image(self) -> str:
        """Image Docker pour Bash"""
        return "bash:latest"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour Bash"""
        return f"bash {file_path}"