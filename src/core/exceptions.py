"""
Gestion des exceptions personnalisées pour Orlyne
"""

class OrlyneError(Exception):
    """Exception de base pour Orlyne"""
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ModelLoadError(OrlyneError):
    """Erreur lors du chargement du modèle"""
    def __init__(self, message: str, model_name: str = None):
        self.model_name = model_name
        super().__init__(
            f"Erreur de chargement du modèle {model_name}: {message}" if model_name else message,
            code=503
        )


class CodeExecutionError(OrlyneError):
    """Erreur lors de l'exécution de code"""
    def __init__(self, message: str, language: str = None, exit_code: int = None):
        self.language = language
        self.exit_code = exit_code
        details = f" [{language}]" if language else ""
        details += f" (code: {exit_code})" if exit_code else ""
        super().__init__(
            f"Erreur d'exécution de code{details}: {message}",
            code=400
        )


class ConfigurationError(OrlyneError):
    """Erreur de configuration"""
    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        key_msg = f" pour {config_key}" if config_key else ""
        super().__init__(
            f"Erreur de configuration{key_msg}: {message}",
            code=500
        )


class PersonalityError(OrlyneError):
    """Erreur liée à la personnalité"""
    def __init__(self, message: str):
        super().__init__(
            f"Erreur de personnalité: {message}",
            code=500
        )


class LearningError(OrlyneError):
    """Erreur lors de l'apprentissage"""
    def __init__(self, message: str, phase: str = None):
        self.phase = phase
        phase_msg = f" pendant {phase}" if phase else ""
        super().__init__(
            f"Erreur d'apprentissage{phase_msg}: {message}",
            code=500
        )


class APIError(OrlyneError):
    """Erreur API"""
    def __init__(self, message: str, endpoint: str = None, status_code: int = 400):
        self.endpoint = endpoint
        endpoint_msg = f" sur {endpoint}" if endpoint else ""
        super().__init__(
            f"Erreur API{endpoint_msg}: {message}",
            code=status_code
        )


class ResourceNotFoundError(OrlyneError):
    """Ressource non trouvée"""
    def __init__(self, resource_type: str, resource_id: str = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        id_msg = f" '{resource_id}'" if resource_id else ""
        super().__init__(
            f"{resource_type}{id_msg} non trouvé",
            code=404
        )


class UnauthorizedError(OrlyneError):
    """Non autorisé"""
    def __init__(self, message: str = "Accès non autorisé"):
        super().__init__(message, code=401)


class RateLimitError(OrlyneError):
    """Limite de taux dépassée"""
    def __init__(self, message: str = "Trop de requêtes", retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(message, code=429)


def handle_exception(e: Exception) -> dict:
    """
    Convertit une exception en réponse JSON
    
    Args:
        e: Exception à traiter
        
    Returns:
        Dictionnaire formaté pour l'API
    """
    if isinstance(e, OrlyneError):
        return {
            "error": e.message,
            "code": e.code,
            "type": e.__class__.__name__
        }
    else:
        return {
            "error": str(e),
            "code": 500,
            "type": "InternalServerError"
        }