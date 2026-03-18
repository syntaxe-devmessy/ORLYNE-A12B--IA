"""
Exécuteur de code Java
"""

import subprocess
import tempfile
import os
import re
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class JavaExecutor(BaseExecutor):
    """Exécute du code Java"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code Java
        
        Args:
            code: Code Java à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            # Extraction du nom de la classe
            class_name = self._extract_class_name(code)
            if not class_name:
                class_name = "Main"
                code = self._wrap_in_class(code, class_name)
            
            # Création du fichier source
            with tempfile.TemporaryDirectory() as temp_dir:
                java_file = os.path.join(temp_dir, f"{class_name}.java")
                with open(java_file, 'w') as f:
                    f.write(code)
                
                # Compilation
                compile_result = subprocess.run(
                    ['javac', java_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=temp_dir
                )
                
                if compile_result.returncode != 0:
                    return {
                        "success": False,
                        "error": compile_result.stderr,
                        "exit_code": compile_result.returncode,
                        "language": "java",
                        "phase": "compilation"
                    }
                
                # Exécution
                exec_result = subprocess.run(
                    ['java', '-cp', '.', class_name],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=temp_dir
                )
                
                return {
                    "success": exec_result.returncode == 0,
                    "output": exec_result.stdout,
                    "error": exec_result.stderr,
                    "exit_code": exec_result.returncode,
                    "language": "java",
                    "phase": "execution"
                }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="java"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="java"
            )
    
    def _extract_class_name(self, code: str) -> str:
        """Extrait le nom de la classe du code Java"""
        match = re.search(r'public\s+class\s+(\w+)', code)
        return match.group(1) if match else None
    
    def _wrap_in_class(self, code: str, class_name: str) -> str:
        """Enveloppe le code dans une classe"""
        return f"""
public class {class_name} {{
    public static void main(String[] args) {{
        {code}
    }}
}}
"""
    
    def get_docker_image(self) -> str:
        """Image Docker pour Java"""
        return "openjdk:17-slim"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour Java"""
        class_name = os.path.splitext(os.path.basename(file_path))[0]
        dir_path = os.path.dirname(file_path)
        return f"javac {file_path} && java -cp {dir_path} {class_name}"