"""
Exécuteur de code Kotlin
"""

import subprocess
import tempfile
import os
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class KotlinExecutor(BaseExecutor):
    """Exécute du code Kotlin"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code Kotlin
        
        Args:
            code: Code Kotlin à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.kt', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Compilation et exécution avec kotlinc
            compile_result = subprocess.run(
                ['kotlinc', temp_file, '-include-runtime', '-d', '/tmp/program.jar'],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if compile_result.returncode == 0:
                # Exécution du JAR
                exec_result = subprocess.run(
                    ['java', '-jar', '/tmp/program.jar'],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                os.unlink(temp_file)
                os.unlink('/tmp/program.jar')
                
                return {
                    "success": exec_result.returncode == 0,
                    "output": exec_result.stdout,
                    "error": exec_result.stderr,
                    "exit_code": exec_result.returncode,
                    "language": "kotlin"
                }
            else:
                os.unlink(temp_file)
                return {
                    "success": False,
                    "error": compile_result.stderr,
                    "exit_code": compile_result.returncode,
                    "language": "kotlin",
                    "phase": "compilation"
                }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="kotlin"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="kotlin"
            )
    
    def get_docker_image(self) -> str:
        """Image Docker pour Kotlin"""
        return "kotlin:latest"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour Kotlin"""
        return f"kotlinc {file_path} -include-runtime -d /tmp/program.jar && java -jar /tmp/program.jar"