"""
Exécuteur de code C++
"""

import subprocess
import tempfile
import os
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class CPPExecutor(BaseExecutor):
    """Exécute du code C++"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code C++
        
        Args:
            code: Code C++ à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Fichier source
                cpp_file = os.path.join(temp_dir, "program.cpp")
                with open(cpp_file, 'w') as f:
                    f.write(code)
                
                # Exécutable
                exe_file = os.path.join(temp_dir, "program")
                
                # Compilation
                compile_result = subprocess.run(
                    ['g++', cpp_file, '-o', exe_file, '-std=c++17'],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                if compile_result.returncode != 0:
                    return {
                        "success": False,
                        "error": compile_result.stderr,
                        "exit_code": compile_result.returncode,
                        "language": "cpp",
                        "phase": "compilation"
                    }
                
                # Exécution
                exec_result = subprocess.run(
                    [exe_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                return {
                    "success": exec_result.returncode == 0,
                    "output": exec_result.stdout,
                    "error": exec_result.stderr,
                    "exit_code": exec_result.returncode,
                    "language": "cpp",
                    "phase": "execution"
                }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="cpp"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="cpp"
            )
    
    def get_docker_image(self) -> str:
        """Image Docker pour C++"""
        return "gcc:latest"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour C++"""
        return f"g++ {file_path} -o /tmp/a.out && /tmp/a.out"