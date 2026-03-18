"""
Débogueur automatique de code multi-langage
"""

import ast
import traceback
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, List, Optional
import subprocess
import tempfile
import os

class CodeDebugger:
    """Débogue automatiquement le code dans différents langages"""
    
    def debug(self, code: str, language: str = "python", error_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Débogue le code fourni
        
        Args:
            code: Code à déboguer
            language: Langage du code
            error_message: Message d'erreur optionnel
            
        Returns:
            Rapport de débogage avec corrections suggérées
        """
        debuggers = {
            "python": self._debug_python,
            "javascript": self._debug_javascript,
            "java": self._debug_java,
            "cpp": self._debug_cpp,
            "default": self._debug_generic
        }
        
        debugger = debuggers.get(language, debuggers["default"])
        return debugger(code, error_message)
    
    def _debug_python(self, code: str, error_message: Optional[str]) -> Dict[str, Any]:
        """Débogue du code Python"""
        issues = []
        suggestions = []
        
        # 1. Vérification syntaxique
        syntax_issues = self._check_python_syntax(code)
        issues.extend(syntax_issues)
        
        # 2. Analyse statique
        static_issues = self._analyze_python_static(code)
        issues.extend(static_issues)
        
        # 3. Exécution test
        execution_result = self._test_execution_python(code)
        
        # 4. Génération des suggestions
        if error_message:
            suggestions.extend(self._generate_suggestions_from_error(error_message))
        
        for issue in issues:
            suggestions.extend(self._generate_suggestions_for_issue(issue))
        
        # 5. Correction automatique
        corrected_code = self._auto_correct_python(code, issues) if issues else code
        
        return {
            "language": "python",
            "has_issues": len(issues) > 0 or not execution_result["success"],
            "issues": issues,
            "suggestions": suggestions,
            "execution_test": execution_result,
            "corrected_code": corrected_code if issues else None,
            "confidence": self._calculate_confidence(issues, execution_result)
        }
    
    def _check_python_syntax(self, code: str) -> List[Dict[str, Any]]:
        """Vérifie la syntaxe Python"""
        issues = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "line": e.lineno,
                "message": str(e),
                "severity": "high"
            })
        except Exception as e:
            issues.append({
                "type": "parsing_error",
                "message": str(e),
                "severity": "high"
            })
        
        return issues
    
    def _analyze_python_static(self, code: str) -> List[Dict[str, Any]]:
        """Analyse statique du code Python"""
        issues = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Variables non utilisées
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    # Vérifier si la variable est utilisée ailleurs
                    pass
                
                # Comparaison avec None
                if isinstance(node, ast.Compare):
                    for op in node.ops:
                        if isinstance(op, (ast.Is, ast.IsNot)):
                            if isinstance(node.comparators[0], ast.Constant) and node.comparators[0].value is None:
                                # C'est correct d'utiliser is/isnot avec None
                                pass
                            else:
                                issues.append({
                                    "type": "style",
                                    "line": node.lineno,
                                    "message": "Utilisez 'is' ou 'is not' uniquement avec None",
                                    "severity": "low"
                                })
                
                # Fonction sans docstring
                if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
                    issues.append({
                        "type": "documentation",
                        "line": node.lineno,
                        "message": f"La fonction '{node.name}' n'a pas de docstring",
                        "severity": "low"
                    })
                
                # Import non utilisé
                # À implémenter avec une analyse de portée
                
        except Exception:
            # Ignorer les erreurs d'analyse si le code a déjà des erreurs de syntaxe
            pass
        
        return issues
    
    def _test_execution_python(self, code: str) -> Dict[str, Any]:
        """Teste l'exécution du code Python"""
        # Capture stdout et stderr
        stdout = StringIO()
        stderr = StringIO()
        
        result = {
            "success": False,
            "output": "",
            "error": "",
            "traceback": ""
        }
        
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exec(code, {"__name__": "__main__"})
            
            result["success"] = True
            result["output"] = stdout.getvalue()
            
        except Exception as e:
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
            result["output"] = stdout.getvalue()
        
        return result
    
    def _generate_suggestions_from_error(self, error_message: str) -> List[str]:
        """Génère des suggestions basées sur un message d'erreur"""
        suggestions = []
        
        # Erreurs Python courantes
        if "NameError" in error_message:
            var_match = error_message.split("'")[1] if "'" in error_message else "inconnue"
            suggestions.append(f"La variable '{var_match}' n'est pas définie. Vérifiez son nom ou définissez-la avant.")
        
        elif "TypeError" in error_message:
            suggestions.append("Erreur de type. Vérifiez que vous utilisez le bon type de données.")
        
        elif "IndexError" in error_message:
            suggestions.append("Index hors limites. Vérifiez la taille de votre liste avant d'accéder à un élément.")
        
        elif "KeyError" in error_message:
            key_match = error_message.split("'")[1] if "'" in error_message else "inconnue"
            suggestions.append(f"La clé '{key_match}' n'existe pas dans le dictionnaire. Vérifiez les clés disponibles.")
        
        elif "AttributeError" in error_message:
            suggestions.append("L'objet n'a pas cet attribut. Vérifiez le nom de l'attribut ou le type de l'objet.")
        
        elif "SyntaxError" in error_message:
            suggestions.append("Erreur de syntaxe. Vérifiez les parenthèses, guillemets et l'indentation.")
        
        elif "IndentationError" in error_message:
            suggestions.append("Erreur d'indentation. Vérifiez que vous utilisez cohéremment des espaces ou des tabulations.")
        
        elif "ImportError" in error_message or "ModuleNotFoundError" in error_message:
            module_match = error_message.split("'")[1] if "'" in error_message else "inconnu"
            suggestions.append(f"Le module '{module_match}' n'est pas installé. Installez-le avec 'pip install {module_match}'")
        
        return suggestions
    
    def _generate_suggestions_for_issue(self, issue: Dict[str, Any]) -> List[str]:
        """Génère des suggestions pour un problème spécifique"""
        suggestions = []
        
        if issue["type"] == "syntax_error":
            suggestions.append("Vérifiez la syntaxe à la ligne indiquée. Une parenthèse, guillemet ou deux-points manque peut-être.")
        
        elif issue["type"] == "style" and "None" in issue["message"]:
            suggestions.append("Utilisez 'is None' pour comparer avec None, pas '== None'.")
        
        elif issue["type"] == "documentation":
            suggestions.append("Ajoutez une docstring pour documenter le but de la fonction et ses paramètres.")
        
        return suggestions
    
    def _auto_correct_python(self, code: str, issues: List[Dict[str, Any]]) -> str:
        """Tente de corriger automatiquement le code Python"""
        lines = code.split('\n')
        
        for issue in issues:
            if issue["type"] == "syntax_error" and "line" in issue:
                line_num = issue["line"] - 1
                if 0 <= line_num < len(lines):
                    line = lines[line_num]
                    
                    # Corrections courantes
                    if "unexpected EOF" in issue["message"]:
                        # Parenthèse manquante
                        if line.count('(') > line.count(')'):
                            lines[line_num] = line + ')'
                    
                    elif "EOL while scanning string literal" in issue["message"]:
                        # Guillemet manquant
                        if line.count('"') % 2 == 1:
                            lines[line_num] = line + '"'
                        elif line.count("'") % 2 == 1:
                            lines[line_num] = line + "'"
        
        return '\n'.join(lines)
    
    def _calculate_confidence(self, issues: List, execution_result: Dict) -> float:
        """Calcule un score de confiance pour les corrections"""
        confidence = 1.0
        
        # Réduction selon la sévérité des problèmes
        for issue in issues:
            if issue["severity"] == "high":
                confidence -= 0.3
            elif issue["severity"] == "medium":
                confidence -= 0.2
            else:
                confidence -= 0.1
        
        # Réduction si l'exécution échoue
        if not execution_result["success"]:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _debug_javascript(self, code: str, error_message: Optional[str]) -> Dict[str, Any]:
        """Débogue du code JavaScript"""
        issues = []
        suggestions = []
        
        # Vérification basique
        lines = code.split('\n')
        
        # Vérification des parenthèses
        parentheses = code.count('(') - code.count(')')
        if parentheses != 0:
            issues.append({
                "type": "syntax_error",
                "message": f"Déséquilibre de parenthèses: {parentheses} parenthèse(s) non fermée(s)",
                "severity": "high"
            })
        
        # Vérification des accolades
        braces = code.count('{') - code.count('}')
        if braces != 0:
            issues.append({
                "type": "syntax_error",
                "message": f"Déséquilibre d'accolades: {braces} accolade(s) non fermée(s)",
                "severity": "high"
            })
        
        # Test d'exécution avec Node.js
        execution_result = self._test_execution_javascript(code)
        
        if error_message:
            suggestions.extend(self._generate_suggestions_from_error_js(error_message))
        
        return {
            "language": "javascript",
            "has_issues": len(issues) > 0 or not execution_result["success"],
            "issues": issues,
            "suggestions": suggestions,
            "execution_test": execution_result
        }
    
    def _test_execution_javascript(self, code: str) -> Dict[str, Any]:
        """Teste l'exécution JavaScript avec Node.js"""
        result = {
            "success": False,
            "output": "",
            "error": ""
        }
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            proc = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            os.unlink(temp_file)
            
            result["success"] = proc.returncode == 0
            result["output"] = proc.stdout
            result["error"] = proc.stderr
            
        except subprocess.TimeoutExpired:
            result["error"] = "Timeout - Le code a pris trop de temps à s'exécuter"
        except FileNotFoundError:
            result["error"] = "Node.js n'est pas installé"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _generate_suggestions_from_error_js(self, error_message: str) -> List[str]:
        """Génère des suggestions pour les erreurs JavaScript"""
        suggestions = []
        
        if "ReferenceError" in error_message:
            suggestions.append("Variable non définie. Vérifiez que vous avez déclaré la variable avec let/const/var.")
        
        elif "TypeError" in error_message:
            suggestions.append("Erreur de type. Vérifiez que vous appelez une fonction sur le bon type d'objet.")
        
        elif "SyntaxError" in error_message:
            suggestions.append("Erreur de syntaxe. Vérifiez les parenthèses, accolades et points-virgules.")
        
        elif "Cannot read property" in error_message:
            suggestions.append("Tentative de lecture d'une propriété sur undefined ou null. Vérifiez que l'objet existe.")
        
        return suggestions
    
    def _debug_java(self, code: str, error_message: Optional[str]) -> Dict[str, Any]:
        """Débogue du code Java"""
        issues = []
        
        # Vérification de la classe principale
        if "public static void main" not in code:
            issues.append({
                "type": "structure",
                "message": "Méthode main manquante. Un programme Java a besoin de 'public static void main(String[] args)'",
                "severity": "high"
            })
        
        # Vérification du nom de classe
        class_match = re.search(r'public\s+class\s+(\w+)', code)
        if not class_match:
            issues.append({
                "type": "structure",
                "message": "Classe publique manquante",
                "severity": "high"
            })
        
        return {
            "language": "java",
            "has_issues": len(issues) > 0,
            "issues": issues,
            "suggestions": [
                "Assurez-vous que le nom du fichier correspond au nom de la classe publique",
                "Vérifiez que tous les points-virgules sont présents",
                "Toute instruction doit être dans une méthode"
            ]
        }
    
    def _debug_cpp(self, code: str, error_message: Optional[str]) -> Dict[str, Any]:
        """Débogue du code C++"""
        issues = []
        
        # Vérification du main
        if "main" not in code:
            issues.append({
                "type": "structure",
                "message": "Fonction main manquante",
                "severity": "high"
            })
        
        # Vérification des includes
        if "#include" not in code and ("cout" in code or "cin" in code):
            issues.append({
                "type": "include",
                "message": "Utilisation de iostream sans #include <iostream>",
                "severity": "medium"
            })
        
        return {
            "language": "cpp",
            "has_issues": len(issues) > 0,
            "issues": issues,
            "suggestions": [
                "Ajoutez #include <iostream> pour utiliser cout/cin",
                "Utilisez 'using namespace std;' ou std::cout",
                "Vérifiez que chaque { a son } correspondant"
            ]
        }
    
    def _debug_generic(self, code: str, error_message: Optional[str]) -> Dict[str, Any]:
        """Débogage générique"""
        return {
            "language": "unknown",
            "has_issues": bool(error_message),
            "issues": [{
                "type": "generic",
                "message": error_message or "Analyse générique - pas de débogage spécifique disponible",
                "severity": "medium"
            }],
            "suggestions": [
                "Vérifiez la syntaxe du code",
                "Assurez-vous que toutes les parenthèses et accolades sont équilibrées",
                "Vérifiez que vous avez déclaré toutes les variables avant de les utiliser"
            ]
        }