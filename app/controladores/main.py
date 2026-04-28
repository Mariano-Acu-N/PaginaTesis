from flask import Blueprint, render_template

class MainController:
    def __init__(self):
        self.main_bp = Blueprint('main', __name__)
        self.register_routes()

    def register_routes(self):
        self.main_bp.route('/')(self.home)
        self.main_bp.route('/faq')(self.faq)
        #self.main_bp.route('/api')(self.api)
        
    def home(self):
        return render_template('index.html')

    def faq(self):
        return render_template('faq.html')

    #def api(self):
    #    return render_template('api.html')