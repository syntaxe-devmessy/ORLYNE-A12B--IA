"""
Analyseur de code multi-langage
"""

import ast
import re
from typing import Dict, Any, List, Optional
import radon.complexity as radon_cc
import radon.metrics as radon_metrics

class CodeAnalyzer:
    """Analyse statique et dynamique de code"""
    
    def analyze(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyse complète du code
        
        Args:
            code: Code à analyser
            language: Langage du code
            
        Returns:
            Rapport d'analyse détaillé
        """
        analyzers = {
            "python": self._analyze_python,
            "javascript": self._analyze_javascript,
            "java": self._analyze_java,
            "cpp": self._analyze_cpp,
            "default": self._analyze_generic
        }
        
        analyzer = analyzers.get(language, analyzers["default"])
        return analyzer(code)
    
    def _analyze_python(self, code: str) -> Dict[str, Any]:
        """Analyse spécifique pour Python"""
        try:
            tree = ast.parse(code)
            
            # Métriques de base
            lines = code.split('\n')
            
            # Complexité cyclomatique
            cc = radon_cc.cc_visit(code)
            
            # Métriques de maintenabilité
            mi = radon_metrics.mi_visit(code, multi=True)
            
            # Analyse des imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
            
            # Détection des fonctions/classes
            functions = []
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "lineno": node.lineno,
                        "args": len(node.args.args),
                        "complexity": len([n for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try))])
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "lineno": node.lineno,
                        "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    })
            
            return {
                "language": "python",
                "stats": {
                    "lines": len(lines),
                    "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
                    "comment_lines": len([l for l in lines if l.strip().startswith('#')]),
                    "empty_lines": len([l for l in lines if not l.strip()])
                },
                "complexity": {
                    "cyclomatic": sum(c.complexity for c in cc),
                    "maintainability_index": mi,
                    "functions": functions,
                    "classes": classes
                },
                "imports": imports,
                "ast": self._ast_to_dict(tree)
            }
            
        except SyntaxError as e:
            return {
                "language": "python",
                "error": f"Erreur de syntaxe: {e}",
                "valid": False
            }
    
    def _analyze_javascript(self, code: str) -> Dict[str, Any]:
        """Analyse basique pour JavaScript"""
        lines = code.split('\n')
        
        # Détection des fonctions
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)|\w+\s*=\s*function\s*\([^)]*\)|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
        functions = re.findall(function_pattern, code)
        
        # Détection des imports
        import_pattern = r'(import|require)\s*\(?[\'"].*[\'"]\)?'
        imports = re.findall(import_pattern, code)
        
        return {
            "language": "javascript",
            "stats": {
                "lines": len(lines),
                "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith('//')]),
                "comment_lines": len([l for l in lines if l.strip().startswith('//') or l.strip().startswith('/*')]),
                "empty_lines": len([l for l in lines if not l.strip()])
            },
            "functions": len([f for f in functions if f]),
            "imports": len(imports)
        }
    
    def _analyze_java(self, code: str) -> Dict[str, Any]:
        """Analyse basique pour Java"""
        lines = code.split('\n')
        
        # Détection des classes
        class_pattern = r'class\s+(\w+)'
        classes = re.findall(class_pattern, code)
        
        # Détection des méthodes
        method_pattern = r'(public|private|protected)?\s+\w+\s+(\w+)\s*\([^)]*\)\s*\{?'
        methods = re.findall(method_pattern, code)
        
        return {
            "language": "java",
            "stats": {
                "lines": len(lines),
                "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('/*')]),
                "comment_lines": len([l for l in lines if l.strip().startswith('//') or l.strip().startswith('/*') or l.strip().startswith('*')]),
                "empty_lines": len([l for l in lines if not l.strip()])
            },
            "classes": classes,
            "methods": len(methods)
        }
    
    def _analyze_cpp(self, code: str) -> Dict[str, Any]:
        """Analyse basique pour C++"""
        lines = code.split('\n')
        
        # Détection des includes
        include_pattern = r'#include\s*[<"][^>"]+[>"]'
        includes = re.findall(include_pattern, code)
        
        return {
            "language": "cpp",
            "stats": {
                "lines": len(lines),
                "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('/*')]),
                "comment_lines": len([l for l in lines if l.strip().startswith('//') or l.strip().startswith('/*') or l.strip().startswith('*')]),
                "empty_lines": len([l for l in lines if not l.strip()])
            },
            "includes": includes
        }
    
    def _analyze_generic(self, code: str) -> Dict[str, Any]:
        """Analyse générique pour tout langage"""
        lines = code.split('\n')
        
        return {
            "language": "unknown",
            "stats": {
                "lines": len(lines),
                "code_lines": len([l for l in lines if l.strip()]),
                "empty_lines": len([l for l in lines if not l.strip()])
            },
            "characters": len(code),
            "words": len(code.split())
        }
    
    def _ast_to_dict(self, node) -> Dict:
        """Convertit un nœud AST en dictionnaire"""
        if isinstance(node, ast.AST):
            result = {
                "_type": node.__class__.__name__,
                "lineno": getattr(node, 'lineno', None),
                "col_offset": getattr(node, 'col_offset', None)
            }
            for field in node._fields:
                value = getattr(node, field)
                result[field] = self._ast_to_dict(value)
            return result
        elif isinstance(node, list):
            return [self._ast_to_dict(item) for item in node]
        else:
            return node