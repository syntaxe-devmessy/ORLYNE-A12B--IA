"""
Explicateur de code multi-langage
"""

import ast
import re
from typing import Dict, Any, List, Optional

class CodeExplainer:
    """Explique le code dans différents langages"""
    
    def explain(self, code: str, language: str = "python", detail_level: str = "medium") -> Dict[str, Any]:
        """
        Explique le code fourni
        
        Args:
            code: Code à expliquer
            language: Langage du code
            detail_level: Niveau de détail (low, medium, high)
            
        Returns:
            Explication structurée du code
        """
        explainers = {
            "python": self._explain_python,
            "javascript": self._explain_javascript,
            "java": self._explain_java,
            "cpp": self._explain_cpp,
            "default": self._explain_generic
        }
        
        explainer = explainers.get(language, explainers["default"])
        return explainer(code, detail_level)
    
    def _explain_python(self, code: str, detail_level: str) -> Dict[str, Any]:
        """Explique du code Python"""
        try:
            tree = ast.parse(code)
            
            # Analyse structurelle
            structure = []
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(self._explain_function(node))
                elif isinstance(node, ast.ClassDef):
                    classes.append(self._explain_class(node))
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(self._explain_import(node))
            
            # Explication ligne par ligne
            lines = self._explain_lines(code, detail_level)
            
            # Résumé général
            summary = self._generate_summary(code, functions, classes, imports)
            
            return {
                "language": "python",
                "summary": summary,
                "structure": structure,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "lines": lines,
                "complexity": self._calculate_complexity(tree)
            }
            
        except SyntaxError as e:
            return {
                "language": "python",
                "error": f"Erreur de syntaxe: {e}",
                "valid": False
            }
    
    def _explain_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Explique une fonction Python"""
        docstring = ast.get_docstring(node)
        
        # Analyse des arguments
        args = []
        for arg in node.args.args:
            args.append({
                "name": arg.arg,
                "annotation": self._get_annotation(arg.annotation)
            })
        
        # Analyse du corps
        body_lines = len(node.body)
        complexity = len([n for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try))])
        
        return {
            "name": node.name,
            "docstring": docstring,
            "args": args,
            "returns": self._get_annotation(node.returns),
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "body_lines": body_lines,
            "complexity": complexity,
            "lineno": node.lineno
        }
    
    def _explain_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Explique une classe Python"""
        docstring = ast.get_docstring(node)
        
        # Analyse des méthodes
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._explain_function(item))
        
        return {
            "name": node.name,
            "docstring": docstring,
            "bases": [self._get_base_name(b) for b in node.bases],
            "methods": methods,
            "lineno": node.lineno
        }
    
    def _explain_import(self, node) -> Dict[str, Any]:
        """Explique un import"""
        if isinstance(node, ast.Import):
            return {
                "type": "import",
                "modules": [alias.name for alias in node.names]
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                "type": "from_import",
                "module": node.module,
                "names": [alias.name for alias in node.names],
                "level": node.level
            }
    
    def _explain_lines(self, code: str, detail_level: str) -> List[Dict[str, Any]]:
        """Explique chaque ligne de code"""
        lines = code.split('\n')
        explanations = []
        
        for i, line in enumerate(lines, 1):
            line = line.rstrip()
            if not line.strip():
                explanations.append({
                    "number": i,
                    "content": line,
                    "type": "empty",
                    "explanation": "Ligne vide"
                })
            elif line.strip().startswith('#'):
                explanations.append({
                    "number": i,
                    "content": line,
                    "type": "comment",
                    "explanation": f"Commentaire: {line.strip('# ')}"
                })
            else:
                # Analyse basique de la ligne
                line_type = self._detect_line_type(line)
                explanation = self._generate_line_explanation(line, line_type, detail_level)
                
                explanations.append({
                    "number": i,
                    "content": line,
                    "type": line_type,
                    "explanation": explanation
                })
        
        return explanations
    
    def _detect_line_type(self, line: str) -> str:
        """Détecte le type d'une ligne de code"""
        if re.match(r'^\s*def\s+\w+\s*\(', line):
            return "function_definition"
        elif re.match(r'^\s*class\s+\w+', line):
            return "class_definition"
        elif re.match(r'^\s*if\s+', line):
            return "conditional"
        elif re.match(r'^\s*(for|while)\s+', line):
            return "loop"
        elif re.match(r'^\s*return\s+', line):
            return "return"
        elif re.match(r'^\s*import\s+', line):
            return "import"
        elif '=' in line and not line.strip().startswith('==')
        elif '=' in line and not line.strip().startswith('=='):
            return "assignment"
        elif re.match(r'^\s*print\s*\(', line):
            return "print"
        elif re.match(r'^\s*try\s*:', line):
            return "try_block"
        elif re.match(r'^\s*except\s*', line):
            return "except_block"
        elif re.match(r'^\s*finally\s*:', line):
            return "finally_block"
        elif re.match(r'^\s*with\s+', line):
            return "context_manager"
        elif re.match(r'^\s*@', line):
            return "decorator"
        else:
            return "statement"

def _generate_line_explanation(self, line: str, line_type: str, detail_level: str) -> str:
    """Génère une explication pour une ligne"""
    explanations = {
        "function_definition": "Définition d'une fonction",
        "class_definition": "Définition d'une classe",
        "conditional": "Structure conditionnelle (if)",
        "loop": "Boucle (for/while)",
        "return": "Retourne une valeur",
        "import": "Importe un module",
        "assignment": "Affectation de variable",
        "print": "Affiche une valeur",
        "try_block": "Début d'un bloc try/except",
        "except_block": "Gestion d'exception",
        "finally_block": "Bloc finally (toujours exécuté)",
        "context_manager": "Gestionnaire de contexte (with)",
        "decorator": "Décorateur",
        "statement": "Instruction simple"
    }
    
    base_explanation = explanations.get(line_type, "Instruction")
    
    if detail_level == "low":
        return base_explanation
    elif detail_level == "medium":
        # Ajoute des détails sur la ligne
        if line_type == "function_definition":
            match = re.search(r'def\s+(\w+)\s*\(([^)]*)\)', line)
            if match:
                return f"Définition de la fonction '{match.group(1)}' avec paramètres: {match.group(2)}"
        elif line_type == "class_definition":
            match = re.search(r'class\s+(\w+)', line)
            if match:
                return f"Définition de la classe '{match.group(1)}'"
        elif line_type == "assignment":
            var_name = line.split('=')[0].strip()
            return f"Affectation à la variable '{var_name}'"
        
        return base_explanation
    else:  # high
        # Explication très détaillée
        return f"{base_explanation} | Ligne: {line.strip()}"

def _get_annotation(self, node) -> Optional[str]:
    """Récupère l'annotation de type"""
    if node is None:
        return None
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Subscript):
        return f"{self._get_annotation(node.value)}[{self._get_annotation(node.slice)}]"
    elif isinstance(node, ast.Attribute):
        return f"{self._get_annotation(node.value)}.{node.attr}"
    elif isinstance(node, ast.Constant):
        return str(node.value)
    return str(node)

def _get_decorator_name(self, node) -> str:
    """Récupère le nom d'un décorateur"""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{self._get_decorator_name(node.value)}.{node.attr}"
    elif isinstance(node, ast.Call):
        return self._get_decorator_name(node.func)
    return str(node)

def _get_base_name(self, node) -> str:
    """Récupère le nom d'une classe de base"""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{self._get_base_name(node.value)}.{node.attr}"
    return str(node)

def _generate_summary(self, code: str, functions: List, classes: List, imports: List) -> str:
    """Génère un résumé du code"""
    lines = len(code.split('\n'))
    
    summary = f"Ce code contient {lines} lignes. "
    
    if functions:
        summary += f"Il définit {len(functions)} fonction(s). "
    if classes:
        summary += f"Il définit {len(classes)} classe(s). "
    if imports:
        summary += f"Il importe {len(imports)} module(s). "
    
    # Détection du type de programme
    if any(f['name'] == 'main' for f in functions):
        summary += "C'est probablement un script exécutable avec une fonction main(). "
    elif classes and not functions:
        summary += "C'est probablement une bibliothèque orientée objet. "
    elif functions and not classes:
        summary += "C'est probablement un ensemble de fonctions utilitaires. "
    
    return summary

def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
    """Calcule la complexité du code"""
    complexity = {
        "if_statements": 0,
        "loops": 0,
        "try_blocks": 0,
        "functions": 0,
        "classes": 0,
        "total": 0
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            complexity["if_statements"] += 1
        elif isinstance(node, (ast.For, ast.While)):
            complexity["loops"] += 1
        elif isinstance(node, ast.Try):
            complexity["try_blocks"] += 1
        elif isinstance(node, ast.FunctionDef):
            complexity["functions"] += 1
        elif isinstance(node, ast.ClassDef):
            complexity["classes"] += 1
    
    complexity["total"] = sum(complexity.values())
    return complexity

def _explain_javascript(self, code: str, detail_level: str) -> Dict[str, Any]:
    """Explique du code JavaScript"""
    lines = code.split('\n')
    
    # Détection des fonctions
    functions = re.findall(r'function\s+(\w+)\s*\([^)]*\)|\w+\s*=\s*function\s*\([^)]*\)|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', code)
    
    # Détection des classes
    classes = re.findall(r'class\s+(\w+)', code)
    
    # Détection des imports
    imports = re.findall(r'(import|require)\s*\(?[\'"].*[\'"]\)?', code)
    
    summary = f"Code JavaScript de {len(lines)} lignes. "
    if functions:
        summary += f"Contient {len([f for f in functions if f])} fonction(s). "
    if classes:
        summary += f"Contient {len(classes)} classe(s). "
    if imports:
        summary += f"Utilise {len(imports)} import(s). "
    
    return {
        "language": "javascript",
        "summary": summary,
        "stats": {
            "lines": len(lines),
            "functions": len([f for f in functions if f]),
            "classes": len(classes),
            "imports": len(imports)
        },
        "lines": self._explain_lines_generic(code, detail_level)
    }

def _explain_java(self, code: str, detail_level: str) -> Dict[str, Any]:
    """Explique du code Java"""
    lines = code.split('\n')
    
    # Détection des classes
    classes = re.findall(r'class\s+(\w+)', code)
    
    # Détection des méthodes
    methods = re.findall(r'(public|private|protected)?\s+\w+\s+(\w+)\s*\([^)]*\)\s*\{?', code)
    
    summary = f"Code Java de {len(lines)} lignes. "
    if classes:
        summary += f"Contient {len(classes)} classe(s). "
    if methods:
        summary += f"Contient {len(methods)} méthode(s). "
    
    return {
        "language": "java",
        "summary": summary,
        "stats": {
            "lines": len(lines),
            "classes": len(classes),
            "methods": len(methods)
        },
        "lines": self._explain_lines_generic(code, detail_level)
    }

def _explain_cpp(self, code: str, detail_level: str) -> Dict[str, Any]:
    """Explique du code C++"""
    lines = code.split('\n')
    
    # Détection des includes
    includes = re.findall(r'#include\s*[<"][^>"]+[>"]', code)
    
    # Détection des fonctions
    functions = re.findall(r'\w+\s+(\w+)\s*\([^)]*\)\s*\{', code)
    
    summary = f"Code C++ de {len(lines)} lignes. "
    if includes:
        summary += f"Inclut {len(includes)} bibliothèque(s). "
    if functions:
        summary += f"Contient {len(functions)} fonction(s). "
    
    return {
        "language": "cpp",
        "summary": summary,
        "stats": {
            "lines": len(lines),
            "includes": len(includes),
            "functions": len(functions)
        },
        "lines": self._explain_lines_generic(code, detail_level)
    }

def _explain_generic(self, code: str, detail_level: str) -> Dict[str, Any]:
    """Explication générique pour tout langage"""
    lines = code.split('\n')
    
    return {
        "language": "unknown",
        "summary": f"Code de {len(lines)} lignes dans un langage non spécifié.",
        "stats": {
            "lines": len(lines),
            "characters": len(code),
            "words": len(code.split())
        },
        "lines": self._explain_lines_generic(code, detail_level)
    }

def _explain_lines_generic(self, code: str, detail_level: str) -> List[Dict[str, Any]]:
    """Explication générique ligne par ligne"""
    lines = code.split('\n')
    explanations = []
    
    for i, line in enumerate(lines, 1):
        line = line.rstrip()
        if not line.strip():
            line_type = "empty"
            explanation = "Ligne vide"
        elif line.strip().startswith(('//', '#', '/*', '*', '--')):
            line_type = "comment"
            explanation = f"Commentaire: {line.strip('#/ *-')}"
        else:
            line_type = "code"
            explanation = "Ligne de code"
        
        explanations.append({
            "number": i,
            "content": line,
            "type": line_type,
            "explanation": explanation
        })
    
    return explanations