"""
Base model and model registry to prevent multiple initializations.
"""
from sqlalchemy.ext.declarative import declared_attr
from app.extensions import db

# Registry to keep track of all models
MODELS_REGISTRY = {}

def register_model(name, model):
    """Register a model in the registry."""
    if name in MODELS_REGISTRY:
        return MODELS_REGISTRY[name]
    MODELS_REGISTRY[name] = model
    return model

class BaseModel(db.Model):
    """Base model class that all models should inherit from."""
    __abstract__ = True
    
    @classmethod
    def register(cls, name):
        """Class decorator to register models."""
        def decorator(model_class):
            return register_model(name, model_class)
        return decorator
        
    def __init__(self, **kwargs):
        # This allows the model to be initialized with keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)
