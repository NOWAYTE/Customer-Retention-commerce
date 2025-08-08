from app.extensions import db
from .base import BaseModel, MODELS_REGISTRY

# Initialize an empty dict to store model references
_models = {}

def get_model(name):
    """Lazy load and return a model by name."""
    if not _models:
        # Import models only when needed
        from .user import User
        from .customer import Customer
        from .segment import CustomerSegment
        
        # Store references to prevent re-imports
        _models.update({
            'User': User,
            'Customer': Customer,
            'CustomerSegment': CustomerSegment
        })
    return _models.get(name)

# Make db and BaseModel available at package level
__all__ = ['db', 'BaseModel', 'get_model'] + list(MODELS_REGISTRY.keys())

# Export registered models in the module's namespace
globals().update(MODELS_REGISTRY)
