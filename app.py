from flask import Flask
from routes import routes_bp
from database import initialize_db, fetch_and_store_products

app = Flask(__name__)

# Initialisation DB + produits
initialize_db()
fetch_and_store_products()

# Routes
app.register_blueprint(routes_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
