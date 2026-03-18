"""
Traducteur de code entre différents langages
"""

import re
from typing import Dict, Any, List, Optional

class CodeTranslator:
    """Traduit du code d'un langage à un autre"""
    
    # Mapping des patterns entre langages
    TRANSLATION_PATTERNS = {
        "python_to_javascript": {
            "print\\((.*?)\\)": r"console.log(\1)",
            "def\\s+(\\w+)\\((.*?)\\):": r"function \1(\2) {",
            "if\\s+(.*?):": r"if (\1) {",
            "elif\\s+(.*?):": r"} else if (\1) {",
            "else:": r"} else {",
            "for\\s+(\\w+)\\s+in\\s+range\\((.*?)\\):": r"for (let \1 = 0; \1 < \2; \1++) {",
            "for\\s+(\\w+)\\s+in\\s+(.*?):": r"for (let \1 in \2) {",
            "while\\s+(.*?):": r"while (\1) {",
            "return\\s+(.*?)$": r"return \1;",
            "True": "true",
            "False": "false",
            "None": "null",
            "and": "&&",
            "or": "||",
            "not": "!",
            "len\\((.*?)\\)": r"\1.length",
            "str\\((.*?)\\)": r"String(\1)",
            "int\\((.*?)\\)": r"parseInt(\1)",
            "float\\((.*?)\\)": r"parseFloat(\1)",
            "list\\((.*?)\\)": r"Array.from(\1)",
            "dict\\((.*?)\\)": r"Object.fromEntries(\1)",
            "append": "push",
            "pop": "pop",
            "remove": "splice"
        },
        
        "javascript_to_python": {
            "console\\.log\\((.*?)\\)": r"print(\1)",
            "function\\s+(\\w+)\\((.*?)\\)\\s*{": r"def \1(\2):",
            "if\\s*\\((.*?)\\)\\s*{": r"if \1:",
            "else\\s+if\\s*\\((.*?)\\)\\s*{": r"elif \1:",
            "else\\s*{": r"else:",
            "for\\s*\\(let\\s+(\\w+)\\s*=\\s*0;\\s*\\1\\s*<\\s*(.*?);\\s*\\1\\+\\+\\)\\s*{": r"for \1 in range(\2):",
            "for\\s*\\(let\\s+(\\w+)\\s+in\\s+(.*?)\\)\\s*{": r"for \1 in \2:",
            "while\\s*\\((.*?)\\)\\s*{": r"while \1:",
            "return\\s+(.*?);": r"return \1",
            "true": "True",
            "false": "False",
            "null": "None",
            "&&": "and",
            "\\|\\|": "or",
            "!": "not",
            "length": "len",
            "String\\((.*?)\\)": r"str(\1)",
            "parseInt\\((.*?)\\)": r"int(\1)",
            "parseFloat\\((.*?)\\)": r"float(\1)",
            "Array\\.from\\((.*?)\\)": r"list(\1)",
            "Object\\.fromEntries\\((.*?)\\)": r"dict(\1)",
            "push": "append",
            "splice": "remove"
        },
        
        "python_to_java": {
            "print\\((.*?)\\)": r"System.out.println(\1);",
            "def\\s+(\\w+)\\((.*?)\\):": r"public static void \1(\2) {",
            "return\\s+(.*?)$": r"return \1;",
            "if\\s+(.*?):": r"if (\1) {",
            "else:": r"} else {",
            "for\\s+(\\w+)\\s+in\\s+range\\((.*?)\\):": r"for (int \1 = 0; \1 < \2; \1++) {",
            "while\\s+(.*?):": r"while (\1) {",
            "True": "true",
            "False": "false",
            "None": "null",
            "len\\((.*?)\\)": r"\1.length",
            "str\\((.*?)\\)": r"String.valueOf(\1)",
            "int\\((.*?)\\)": r"Integer.parseInt(\1)"
        },
        
        "python_to_cpp": {
            "print\\((.*?)\\)": r"std::cout << \1 << std::endl;",
            "def\\s+(\\w+)\\((.*?)\\):": r"void \1(\2) {",
            "return\\s+(.*?)$": r"return \1;",
            "if\\s+(.*?):": r"if (\1) {",
            "else:": r"} else {",
            "for\\s+(\\w+)\\s+in\\s+range\\((.*?)\\):": r"for (int \1 = 0; \1 < \2; \1++) {",
            "while\\s+(.*?):": r"while (\1) {",
            "True": "true",
            "False": "false",
            "None": "nullptr",
            "len\\((.*?)\\)": r"\1.size()",
            "str\\((.*?)\\)": r"std::to_string(\1)",
            "int\\((.*?)\\)": r"std::stoi(\1)"
        },
        
        "java_to_python": {
            "System\\.out\\.println\\((.*?)\\);": r"print(\1)",
            "public\\s+static\\s+void\\s+(\\w+)\\((.*?)\\)\\s*{": r"def \1(\2):",
            "return\\s+(.*?);": r"return \1",
            "if\\s*\\((.*?)\\)\\s*{": r"if \1:",
            "else\\s*{": r"else:",
            "for\\s*\\(int\\s+(\\w+)\\s*=\\s*0;\\s*\\1\\s*<\\s*(.*?);\\s*\\1\\+\\+\\)\\s*{": r"for \1 in range(\2):",
            "while\\s*\\((.*?)\\)\\s*{": r"while \1:",
            "true": "True",
            "false": "False",
            "null": "None",
            "length": "len",
            "String\\.valueOf\\((.*?)\\)": r"str(\1)",
            "Integer\\.parseInt\\((.*?)\\)": r"int(\1)"
        }
    }
    
    def translate(self, code: str, from_language: str, to_language: str) -> Dict[str, Any]:
        """
        Traduit du code d'un langage à un autre
        
        Args:
            code: Code à traduire
            from_language: Langage source
            to_language: Langage cible
            
        Returns:
            Code traduit et métadonnées
        """
        # Création de la clé de traduction
        translation_key = f"{from_language}_to_{to_language}"
        
        if translation_key in self.TRANSLATION_PATTERNS:
            patterns = self.TRANSLATION_PATTERNS[translation_key]
            translated_code = self._apply_translations(code, patterns)
            
            # Ajout des ajustements spécifiques
            translated_code = self._apply_specific_adjustments(
                translated_code, from_language, to_language
            )
            
            return {
                "success": True,
                "translated_code": translated_code,
                "from_language": from_language,
                "to_language": to_language,
                "warnings": self._generate_warnings(code, from_language, to_language)
            }
        else:
            # Traduction via règles génériques
            return {
                "success": False,
                "error": f"Traduction de {from_language} vers {to_language} non disponible",
                "from_language": from_language,
                "to_language": to_language,
                "suggestion": "Utilisez l'API de chat pour une traduction plus précise"
            }
    
    def _apply_translations(self, code: str, patterns: Dict[str, str]) -> str:
        """Applique les patterns de traduction"""
        result = code
        
        for pattern, replacement in patterns.items():
            try:
                result = re.sub(pattern, replacement, result, flags=re.MULTILINE)
            except re.error:
                # Ignorer les patterns invalides
                continue
        
        return result
    
    def _apply_specific_adjustments(self, code: str, from_lang: str, to_lang: str) -> str:
        """Applique des ajustements spécifiques selon les langages"""
        lines = code.split('\n')
        adjusted_lines = []
        
        if from_lang == "python" and to_lang == "javascript":
            for line in lines:
                # Ajustement de l'indentation
                if line.strip() and not line.strip().startswith(('function', 'if', 'for', 'while')):
                    # Supprimer les deux-points à la fin
                    if line.rstrip().endswith(':'):
                        line = line.rstrip()[:-1]
                
                # Ajouter des points-virgules si nécessaire
                if line.strip() and not line.strip().endswith(('{', '}', ';')):
                    if not line.strip().startswith(('function', 'if', 'for', 'while')):
                        line += ';'
                
                adjusted_lines.append(line)
        
        elif from_lang == "javascript" and to_lang == "python":
            for line in lines:
                # Remplacer les points-virgules
                line = line.rstrip().rstrip(';')
                
                # Ajuster l'indentation
                if line.strip() and not line.strip().startswith(('def', 'if', 'elif', 'else', 'for', 'while')):
                    # Ajouter les deux-points pour les structures de contrôle
                    if line.strip().startswith(('if', 'for', 'while')):
                        line += ':'
                
                adjusted_lines.append(line)
        
        else:
            adjusted_lines = lines
        
        return '\n'.join(adjusted_lines)
    
    def _generate_warnings(self, code: str, from_lang: str, to_lang: str) -> List[str]:
        """Génère des avertissements sur la traduction"""
        warnings = []
        
        # Avertissements génériques
        warnings.append("La traduction automatique peut ne pas être parfaite")
        warnings.append("Vérifiez la syntaxe et la logique après traduction")
        
        # Avertissements spécifiques
        if from_lang == "python" and to_lang == "javascript":
            warnings.append("Les classes Python sont traduites en fonctions JavaScript - vérifiez l'héritage")
            warnings.append("Les décorateurs Python n'ont pas d'équivalent direct en JavaScript")
        
        elif from_lang == "javascript" and to_lang == "python":
            warnings.append("Les promesses JavaScript sont traduites en code synchrone - vérifiez l'asynchrone")
            warnings.append("Les prototypes JavaScript sont traduits en classes Python")
        
        elif from_lang == "python" and to_lang == "java":
            warnings.append("Java est typé statiquement - ajoutez les types manuellement")
            warnings.append("Les fonctions Python deviennent des méthodes static en Java")
        
        return warnings
    
    def detect_language(self, code: str) -> str:
        """Détecte le langage du code"""
        score = {
            "python": 0,
            "javascript": 0,
            "java": 0,
            "cpp": 0,
            "ruby": 0,
            "php": 0,
            "unknown": 0
        }
        
        # Patterns pour chaque langage
        patterns = {
            "python": [
                (r'def\s+\w+\s*\(', 10),
                (r'import\s+\w+', 5),
                (r'from\s+\w+\s+import', 5),
                (r'print\(', 3),
                (r'if\s+__name__\s*==\s*["\']__main__["\']', 10),
                (r':\s*$', 2),
                (r'#.*$', 1),
                (r'None|True|False', 2)
            ],
            "javascript": [
                (r'function\s+\w+\s*\(', 10),
                (r'const|let|var\s+\w+\s*=', 5),
                (r'console\.log\(', 5),
                (r'=>', 5),
                (r'document\.|window\.', 3),
                (r'{\s*$', 2),
                (r'}\s*$', 2),
                (r'//.*$', 1),
                (r'null|undefined', 2)
            ],
            "java": [
                (r'public\s+class\s+\w+', 10),
                (r'public\s+static\s+void\s+main', 10),
                (r'System\.out\.println', 5),
                (r'import\s+java\.', 5),
                (r'@Override', 5),
                (r';\s*$', 2),
                (r'//.*$', 1),
                (r'/\*.*?\*/', 1)
            ],
            "cpp": [
                (r'#include\s*[<"][^>"]+[>"]', 10),
                (r'std::', 5),
                (r'cout|cin|endl', 5),
                (r'int\s+main\s*\(', 10),
                (r'->', 3),
                (r'::', 3),
                (r'//.*$', 1),
                (r'/\*.*?\*/', 1)
            ],
            "ruby": [
                (r'def\s+\w+', 5),
                (r'end\s*$', 5),
                (r'puts\s+', 3),
                (r'require\s+', 3),
                (r'#.*$', 1),
                (r'@\w+', 2)
            ],
            "php": [
                (r'<\?php', 10),
                (r'\$[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*', 5),
                (r'echo\s+', 3),
                (r'function\s+\w+\s*\(', 5),
                (r'//.*$', 1),
                (r'/\*.*?\*/', 1)
            ]
        }
        
        # Calcul du score
        for lang, lang_patterns in patterns.items():
            for pattern, weight in lang_patterns:
                if re.search(pattern, code, re.MULTILINE):
                    score[lang] += weight
        
        # Détection du langage avec le score le plus élevé
        detected = max(score.items(), key=lambda x: x[1])
        
        if detected[1] == 0:
            return "unknown"
        
        return detected[0]