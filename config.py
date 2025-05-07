# config.py

import os
from dotenv import load_dotenv

load_dotenv()     # carga .env antes de leer variables

class Config:
    SECRET_KEY  = os.getenv('SECRET_KEY', 'secreta')
    DB_SERVER   = os.getenv('DB_SERVER')    # puede ser None aquí, pero no hacemos split
    DB_NAME     = os.getenv('DB_NAME')
    DB_USER     = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    # Solo valores estáticos o directamente tomados del entorno
    DATABASE_CONFIG = {
        'DRIVER': '{ODBC Driver 17 for SQL Server}',
        'SERVER': None,      # lo rellenamos abajo
        'DATABASE': None,    # lo rellenamos abajo
        'UID': None,         # idem
        'PWD': None,
        'Encrypt': 'yes',
        'TrustServerCertificate': 'yes',
        'Connection Timeout': '30'
    }

    @staticmethod
    def get_connection_string():
        # 1) Comprueba que las vars estén definidas
        missing = [var for var in ('DB_SERVER','DB_NAME','DB_USER','DB_PASSWORD')
                   if getattr(Config, var) is None]
        if missing:
            raise RuntimeError(f"Falta definir en el entorno: {missing}")

        # 2) Prepara el mapa definitivo
        cfg = Config.DATABASE_CONFIG.copy()
        cfg['SERVER'] = f"tcp:{Config.DB_SERVER},1433"
        cfg['DATABASE'] = Config.DB_NAME
        # split seguro ahora que DB_SERVER no es None
        server_base = Config.DB_SERVER.split('.')[0]
        cfg['UID'] = f"{Config.DB_USER}@{server_base}"
        cfg['PWD'] = Config.DB_PASSWORD

        # 3) Arma el string
        return (
            f"Driver={cfg['DRIVER']};"
            f"Server={cfg['SERVER']};"
            f"Database={cfg['DATABASE']};"
            f"Uid={cfg['UID']};"
            f"Pwd={cfg['PWD']};"
            f"Encrypt={cfg['Encrypt']};"
            f"TrustServerCertificate={cfg['TrustServerCertificate']};"
            f"Connection Timeout={cfg['Connection Timeout']};"
        )
