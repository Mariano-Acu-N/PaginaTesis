from app.start import start_app

class Run:
    def __init__(self):
        self.app = start_app().create_app()

    def run_app(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    runner = Run()
    runner.run_app()        
