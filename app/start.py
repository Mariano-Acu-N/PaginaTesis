from flask import Flask
from app.config import Config
from app.controladores.main import MainController
from app.controladores.api import ApiController

class start_app:
    def __init__(self):
        self.config = Config
        self.app = Flask(__name__)
        self.main_bp = MainController().main_bp
        self.api_bp = ApiController().api_bp
        self.configure_app()
        self.register_blueprints()

    def configure_app(self):
        self.app.config.from_object(Config)

    def register_blueprints(self):
        self.app.register_blueprint(self.main_bp)
        self.app.register_blueprint(self.api_bp)

    def create_app(self):
        return self.app    
