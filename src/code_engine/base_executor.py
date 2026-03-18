"""
Classe de base pour tous les exécuteurs de code
"""

from abc import ABC, abstractmethod
import subprocess
import tempfile
import os
import docker
from typing import Dict, Any, Optional
import logging

from src.core.exceptions import CodeExecutionError
from src.core.config import Config

logger = logging.getLogger(__name__)

class BaseExecutor(ABC):
    """Classe abstraite pour l'exécution de code"""
    
    def __init__(self, use_docker: bool = True):
        self.config = Config()
        self.use_docker = use_docker and self.config.code_engine.use_docker
        self.docker_client = None
        
        if self.use_docker:
            try:
                self.docker_client = docker.from_env()
            except Exception as e:
                logger.warning(f"Docker non disponible: {e}")
                self.use_docker = False
    
    @abstractmethod
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute du code dans le langage spécifique
        
        Args:
            code: Code à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        pass
    
    @abstractmethod
    def get_docker_image(self) -> str:
        """Retourne l'image Docker pour ce langage"""
        pass
    
    @abstractmethod
    def get_docker_command(self, file_path: str) -> str:
        """Retourne la commande Docker pour exécuter le code"""
        pass
    
    def execute_with_docker(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute le code dans un conteneur Docker
        
        Args:
            code: Code à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        if not self.docker_client:
            return {
                "success": False,
                "error": "Docker non disponible",
                "fallback_to_native": True
            }
        
        try:
            # Création d'un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(), delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Montage du fichier dans le conteneur
            container_name = f"orlyne_exec_{os.path.basename(temp_file)}"
            mount_path = f"/app/{os.path.basename(temp_file)}"
            
            # Configuration du conteneur
            container = self.docker_client.containers.run(
                image=self.get_docker_image(),
                command=self.get_docker_command(mount_path),
                volumes={os.path.dirname(temp_file): {'bind': '/app', 'mode': 'ro'}},
                detach=True,
                mem_limit=f"{self.config.code_engine.max_memory_mb}m",
                cpu_period=100000,
                cpu_quota=int(self.config.code_engine.max_cpu_cores * 100000),
                network_disabled=not self.config.code_engine.network_enabled,
                read_only=True
            )
            
            # Attente du résultat
            result = container.wait(timeout=timeout)
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            
            # Nettoyage
            container.remove()
            os.unlink(temp_file)
            
            return {
                "success": result['StatusCode'] == 0,
                "output": logs,
                "exit_code": result['StatusCode'],
                "execution_method": "docker",
                "container_id": container.id
            }
            
        except docker.errors.APIError as e:
            logger.error(f"Erreur Docker: {e}")
            return {
                "success": False,
                "error": f"Erreur Docker: {e}",
                "execution_method": "docker"
            }
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_method": "docker"
            }
    
    def _get_file_extension(self) -> str:
        """Retourne l'extension de fichier pour ce langage"""
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c',
            'rust': '.rs',
            'go': '.go',
            'ruby': '.rb',
            'php': '.php',
            'swift': '.swift',
            'kotlin': '.kt',
            'bash': '.sh',
            'powershell': '.ps1',
            'sql': '.sql'
        }
        
        class_name = self.__class__.__name__.lower()
        for lang, ext in extensions.items():
            if lang in class_name:
                return ext
        
        return '.txt'
    
    def _check_dependencies(self, commands: list) -> bool:
        """Vérifie si les dépendances sont installées"""
        for cmd in commands:
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
        return True
    
    def _create_sandbox(self) -> tempfile.TemporaryDirectory:
        """Crée un environnement sandboxé pour l'exécution"""
        return tempfile.TemporaryDirectory()