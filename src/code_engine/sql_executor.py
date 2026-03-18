"""
Exécuteur de requêtes SQL
"""

import sqlite3
import tempfile
import os
from typing import Dict, Any, List
import pandas as pd

from src.code_engine.base_executor import BaseExecutor
from src.core.exceptions import CodeExecutionError

class SQLExecutor(BaseExecutor):
    """Exécute des requêtes SQL"""
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Exécute une ou plusieurs requêtes SQL
        
        Args:
            code: Requêtes SQL à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution
        """
        try:
            # Création d'une base temporaire en mémoire
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            
            # Séparation des requêtes
            queries = self._split_queries(code)
            results = []
            
            for query in queries:
                if query.strip():
                    try:
                        cursor.execute(query)
                        
                        # Récupération des résultats si SELECT
                        if query.strip().upper().startswith('SELECT'):
                            columns = [description[0] for description in cursor.description]
                            rows = cursor.fetchall()
                            
                            # Conversion en DataFrame pour un affichage plus propre
                            df = pd.DataFrame(rows, columns=columns)
                            results.append({
                                "type": "select",
                                "columns": columns,
                                "rows": rows,
                                "row_count": len(rows),
                                "formatted": df.to_string()
                            })
                        else:
                            # Pour INSERT, UPDATE, DELETE, etc.
                            results.append({
                                "type": "modification",
                                "affected_rows": cursor.rowcount,
                                "last_rowid": cursor.lastrowid
                            })
                            
                    except sqlite3.Error as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "query": query,
                            "results": results,
                            "language": "sql"
                        }
            
            conn.close()
            
            return {
                "success": True,
                "results": results,
                "query_count": len(queries),
                "language": "sql"
            }
            
        except Exception as e:
            raise CodeExecutionError(
                str(e),
                language="sql"
            )
    
    def _split_queries(self, sql: str) -> List[str]:
        """Sépare les requêtes SQL par point-virgule"""
        queries = []
        current_query = []
        in_string = False
        string_char = None
        
        for char in sql:
            if char in ['"', "'"] and not in_string:
                in_string = True
                string_char = char
                current_query.append(char)
            elif char == string_char and in_string:
                in_string = False
                string_char = None
                current_query.append(char)
            elif char == ';' and not in_string:
                queries.append(''.join(current_query))
                current_query = []
            else:
                current_query.append(char)
        
        # Ajouter la dernière requête si elle existe
        if current_query:
            queries.append(''.join(current_query))
        
        return [q.strip() for q in queries if q.strip()]
    
    def get_docker_image(self) -> str:
        """Image Docker pour SQL"""
        return "mysql:8.0"
    
    def get_docker_command(self, file_path: str) -> str:
        """Commande Docker pour SQL"""
        return f"mysql -u root -e 'source {file_path}'"