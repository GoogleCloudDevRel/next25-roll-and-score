import logging
import os

from flask import Flask
from routes import api_blueprint

# Initialize flask app
app = Flask(__name__)

# Register blueprint to the app with prefix '/api'
app.register_blueprint(api_blueprint, url_prefix='/api')

# Configure base logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    app.run(
        debug=os.environ.get('DEBUG', False),
        host='0.0.0.0',
        port=8080
    )
