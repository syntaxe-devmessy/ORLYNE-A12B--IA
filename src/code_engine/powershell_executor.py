"""
Exécuteur de scripts PowerShell
"""

import subprocess
import tempfile
import os
import sys
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class PowerShellExecutor(BaseExecutor):
    """Exécute des scripts PowerShell"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute un script PowerShell
        
        Args:
            code: Script PowerShell à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Détection du système d'exploitation
            if sys.platform == 'win32':
                # Windows : PowerShell natif
                result = subprocess.run(
                    ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                # Linux/Mac : PowerShell Core
                result = subprocess.run(
                    ['pwsh', '-File', temp_file],
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
                "language": "powershell"
            }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="powershell"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="powershell"
            )
    
    def get_docker_image(self) -> str:
        """Image Docker pour PowerShell"""
        return "mcr.microsoft.com/powershell:latest"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour PowerShell"""
        return f"pwsh -File {file_path}"