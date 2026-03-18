"""
Moteur d'exécution de code multi-langage
Sans restrictions - exécute TOUT type de code
"""

import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
import logging
import docker
import asyncio

logger = logging.getLogger(__name__)

class CodeExecutor:
    """Exécute du code dans différents langages sans restrictions"""
    
    def __init__(self, use_docker: bool = True):
        self.use_docker = use_docker
        self.docker_client = docker.from_env() if use_docker else None
        
        # Configuration des exécuteurs par langage
        self.executors = {
            "python": self._execute_python,
            "javascript": self._execute_javascript,
            "typescript": self._execute_typescript,
            "java": self._execute_java,
            "cpp": self._execute_cpp,
            "c": self._execute_c,
            "rust": self._execute_rust,
            "go": self._execute_go,
            "ruby": self._execute_ruby,
            "php": self._execute_php,
            "swift": self._execute_swift,
            "kotlin": self._execute_kotlin,
            "bash": self._execute_bash,
            "powershell": self._execute_powershell,
            "sql": self._execute_sql,
            "html": self._execute_html,
            "css": self._execute_css,
            "r": self._execute_r,
            "perl": self._execute_perl,
            "lua": self._execute_lua,
            "dart": self._execute_dart,
            "elixir": self._execute_elixir,
            "haskell": self._execute_haskell,
            "scala": self._execute_scala,
            "julia": self._execute_julia,
            "matlab": self._execute_matlab,
        }
    
    def execute(self, code: str, language: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code dans le langage spécifié
        
        Args:
            code: Code à exécuter
            language: Langage de programmation
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        language = language.lower()
        
        if language not in self.executors:
            return {
                "success": False,
                "error": f"Langage non supporté: {language}",
                "supported_languages": list(self.executors.keys())
            }
        
        try:
            # Exécution du code
            if self.use_docker:
                result = self._execute_in_docker(code, language, timeout)
            else:
                result = self.executors[language](code, timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur d'exécution {language}: {e}")
            return {
                "success": False,
                "error": str(e),
                "language": language
            }
    
    def _execute_in_docker(self, code: str, language: str, timeout: int) -> Dict[str, Any]:
        """Exécute le code dans un conteneur Docker"""
        try:
            # Création d'un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_extension(language), delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Commande d'exécution selon le langage
            cmd = self._get_docker_command(language, temp_file)
            
            # Exécution dans Docker
            container = self.docker_client.containers.run(
                image=self._get_docker_image(language),
                command=cmd,
                remove=True,
                detach=True,
                mem_limit="512m",
                cpu_period=100000,
                cpu_quota=50000,  # 0.5 CPU
                network_disabled=True,  # Pas de réseau par sécurité
                read_only=True  # Système de fichiers en lecture seule
            )
            
            # Attente du résultat
            result = container.wait(timeout=timeout)
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            
            # Nettoyage
            os.unlink(temp_file)
            
            return {
                "success": result['StatusCode'] == 0,
                "output": logs,
                "exit_code": result['StatusCode'],
                "language": language,
                "execution_method": "docker"
            }
            
        except docker.errors.APIError as e:
            return {
                "success": False,
                "error": f"Erreur Docker: {e}",
                "language": language
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "language": language
            }
    
    def _execute_python(self, code: str, timeout: int) -> Dict[str, Any]:
        """Exécute du code Python"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                ['python3', temp_file],
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
                "language": "python"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Timeout dépassé ({timeout}s)",
                "language": "python"
            }
    
    def _execute_javascript(self, code: str, timeout: int) -> Dict[str, Any]:
        """Exécute du code JavaScript (Node.js)"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                ['node', temp_file],
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
                "language": "javascript"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Timeout dépassé ({timeout}s)",
                "language": "javascript"
            }
    
    def _get_extension(self, language: str) -> str:
        """Retourne l'extension de fichier pour un langage"""
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java",
            "cpp": ".cpp",
            "c": ".c",
            "rust": ".rs",
            "go": ".go",
            "ruby": ".rb",
            "php": ".php",
            "swift": ".swift",
            "kotlin": ".kt",
            "bash": ".sh",
            "powershell": ".ps1",
            "r": ".r",
            "perl": ".pl",
            "lua": ".lua",
            "dart": ".dart",
            "elixir": ".exs",
            "haskell": ".hs",
            "scala": ".scala",
            "julia": ".jl",
        }
        return extensions.get(language, ".txt")
    
    def _get_docker_image(self, language: str) -> str:
        """Retourne l'image Docker pour un langage"""
        images = {
            "python": "python:3.11-slim",
            "javascript": "node:18-slim",
            "typescript": "node:18-slim",
            "java": "openjdk:17-slim",
            "cpp": "gcc:latest",
            "c": "gcc:latest",
            "rust": "rust:1.70-slim",
            "go": "golang:1.20-slim",
            "ruby": "ruby:3.2-slim",
            "php": "php:8.2-cli",
            "swift": "swift:5.8-slim",
            "kotlin": "kotlin:latest",
            "bash": "bash:latest",
            "r": "r-base:latest",
        }
        return images.get(language, "alpine:latest")
    
    def _get_docker_command(self, language: str, file_path: str) -> str:
        """Retourne la commande Docker pour exécuter le code"""
        commands = {
            "python": f"python {file_path}",
            "javascript": f"node {file_path}",
            "typescript": f"ts-node {file_path}",
            "java": f"java {file_path}",
            "cpp": f"g++ {file_path} -o /tmp/a.out && /tmp/a.out",
            "c": f"gcc {file_path} -o /tmp/a.out && /tmp/a.out",
            "rust": f"rustc {file_path} -o /tmp/out && /tmp/out",
            "go": f"go run {file_path}",
            "ruby": f"ruby {file_path}",
            "php": f"php {file_path}",
            "bash": f"bash {file_path}",
        }
        return commands.get(language, f"cat {file_path}")