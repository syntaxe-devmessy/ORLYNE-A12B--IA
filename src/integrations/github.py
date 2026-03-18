"""
Intégration GitHub pour Orlyne
"""

import os
import logging
from typing import Dict, List, Optional, Any
from github import Github, GithubException
from github.Repository import Repository
from github.ContentFile import ContentFile
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubIntegration:
    """Intégration avec GitHub"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.client = None
        self.authenticated = False
        
        if self.token:
            self.authenticate()
    
    def authenticate(self):
        """Authentification à GitHub"""
        try:
            self.client = Github(self.token)
            user = self.client.get_user()
            self.authenticated = True
            logger.info(f"Authentifié sur GitHub en tant que {user.login}")
        except Exception as e:
            logger.error(f"Erreur authentification GitHub: {e}")
            self.authenticated = False
    
    def get_repo(self, repo_name: str) -> Optional[Repository]:
        """Récupère un dépôt"""
        if not self.authenticated:
            return None
        
        try:
            return self.client.get_repo(repo_name)
        except GithubException as e:
            logger.error(f"Erreur récupération dépôt {repo_name}: {e}")
            return None
    
    def get_file_content(self, repo_name: str, file_path: str) -> Optional[str]:
        """Récupère le contenu d'un fichier"""
        repo = self.get_repo(repo_name)
        if not repo:
            return None
        
        try:
            content = repo.get_contents(file_path)
            if isinstance(content, list):
                return None
            
            # Décodage du contenu
            if content.encoding == 'base64':
                return base64.b64decode(content.content).decode('utf-8')
            return content.content
        except Exception as e:
            logger.error(f"Erreur lecture fichier {file_path}: {e}")
            return None
    
    def create_file(self, repo_name: str, file_path: str, content: str, 
                   commit_message: str, branch: str = "main") -> bool:
        """Crée un fichier dans le dépôt"""
        repo = self.get_repo(repo_name)
        if not repo:
            return False
        
        try:
            repo.create_file(
                file_path,
                commit_message,
                content,
                branch=branch
            )
            logger.info(f"Fichier créé: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur création fichier: {e}")
            return False
    
    def update_file(self, repo_name: str, file_path: str, content: str,
                   commit_message: str, branch: str = "main") -> bool:
        """Met à jour un fichier"""
        repo = self.get_repo(repo_name)
        if not repo:
            return False
        
        try:
            contents = repo.get_contents(file_path, ref=branch)
            repo.update_file(
                file_path,
                commit_message,
                content,
                contents.sha,
                branch=branch
            )
            logger.info(f"Fichier mis à jour: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur mise à jour fichier: {e}")
            return False
    
    def search_code(self, query: str, language: Optional[str] = None) -> List[Dict]:
        """Recherche du code sur GitHub"""
        if not self.authenticated:
            return []
        
        try:
            if language:
                query = f"{query} language:{language}"
            
            result = self.client.search_code(query)
            
            results = []
            for item in result[:10]:  # Limite à 10 résultats
                results.append({
                    "name": item.name,
                    "path": item.path,
                    "repository": item.repository.full_name,
                    "url": item.html_url,
                    "language": language
                })
            
            return results
        except Exception as e:
            logger.error(f"Erreur recherche code: {e}")
            return []
    
    def get_repo_structure(self, repo_name: str, path: str = "") -> List[Dict]:
        """Récupère la structure d'un dépôt"""
        repo = self.get_repo(repo_name)
        if not repo:
            return []
        
        try:
            contents = repo.get_contents(path)
            structure = []
            
            for content in contents:
                item = {
                    "name": content.name,
                    "path": content.path,
                    "type": content.type,
                    "size": content.size,
                    "url": content.html_url
                }
                
                if content.type == "dir":
                    item["children"] = self.get_repo_structure(repo_name, content.path)
                
                structure.append(item)
            
            return structure
        except Exception as e:
            logger.error(f"Erreur structure dépôt: {e}")
            return []
    
    def create_gist(self, description: str, files: Dict[str, str], 
                   public: bool = False) -> Optional[str]:
        """Crée un gist"""
        if not self.authenticated:
            return None
        
        try:
            gist = self.client.get_user().create_gist(
                public=public,
                files=files,
                description=description
            )
            logger.info(f"Gist créé: {gist.html_url}")
            return gist.html_url
        except Exception as e:
            logger.error(f"Erreur création gist: {e}")
            return None
    
    def get_user_repos(self) -> List[Dict]:
        """Récupère les dépôts de l'utilisateur"""
        if not self.authenticated:
            return []
        
        try:
            repos = self.client.get_user().get_repos()
            return [{
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "url": repo.html_url,
                "private": repo.private
            } for repo in repos[:20]]
        except Exception as e:
            logger.error(f"Erreur récupération repos: {e}")
            return []
    
    def analyze_repo(self, repo_name: str) -> Dict[str, Any]:
        """Analyse un dépôt"""
        repo = self.get_repo(repo_name)
        if not repo:
            return {"error": "Dépôt non trouvé"}
        
        try:
            # Statistiques de base
            stats = {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "language": repo.language,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                "size": repo.size,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "open_issues": repo.open_issues_count,
                "subscribers": repo.subscribers_count,
                "default_branch": repo.default_branch,
                "license": repo.license.name if repo.license else None
            }
            
            # Langages utilisés
            languages = repo.get_languages()
            stats["languages"] = languages
            
            # Derniers commits
            commits = []
            for commit in repo.get_commits()[:5]:
                commits.append({
                    "sha": commit.sha[:8],
                    "message": commit.commit.message,
                    "author": commit.commit.author.name,
                    "date": commit.commit.author.date.isoformat()
                })
            stats["recent_commits"] = commits
            
            # README
            try:
                readme = repo.get_readme()
                stats["has_readme"] = True
                stats["readme_size"] = readme.size
            except:
                stats["has_readme"] = False
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur analyse dépôt: {e}")
            return {"error": str(e)}