from flask import Flask
from Controller import blueprints
from config import Config

# Inicializar Flask
app = Flask(__name__, static_folder='static', template_folder="View/templates")
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY  # Usa la clave del archivo de configuración

# Registrar Blueprints
for blueprint in blueprints:
    app.register_blueprint(blueprint)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
