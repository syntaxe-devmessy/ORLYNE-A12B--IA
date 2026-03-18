"""
Exécuteur de code Rust
"""

import subprocess
import tempfile
import os
from typing import Dict, Any

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class RustExecutor(BaseExecutor):
    """Exécute du code Rust"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code Rust
        
        Args:
            code: Code Rust à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Création d'un projet Cargo minimal
                src_dir = os.path.join(temp_dir, "src")
                os.makedirs(src_dir)
                
                # Fichier main.rs
                rs_file = os.path.join(src_dir, "main.rs")
                with open(rs_file, 'w') as f:
                    f.write(code)
                
                # Cargo.toml
                cargo_toml = os.path.join(temp_dir, "Cargo.toml")
                with open(cargo_toml, 'w') as f:
                    f.write("""
[package]
name = "temp_program"
version = "0.1.0"
edition = "2021"

[dependencies]
""")
                
                # Compilation et exécution
                result = subprocess.run(
                    ['cargo', 'run', '--quiet'],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=temp_dir
                )
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "exit_code": result.returncode,
                    "language": "rust"
                }
            
        except subprocess.TimeoutExpired:
            raise CodeExecutionError(
                f"Timeout dépassé ({timeout}s)",
                language="rust"
            )
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="rust"
            )
    
    def get_docker_image(self) -> str:
        """Image Docker pour Rust"""
        return "rust:1.70-slim"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour Rust"""
        return f"rustc {file_path} -o /tmp/out && /tmp/out"