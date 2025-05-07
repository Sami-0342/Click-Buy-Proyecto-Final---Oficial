from flask import Blueprint

from .main_routes import main_routes
from .auth_routes import auth_bp  
from .product_routes import product_bp

# Lista de blueprints
blueprints = [main_routes, auth_bp, product_bp]