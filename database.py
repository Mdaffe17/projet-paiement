from peewee import PostgresqlDatabase
import os

# Connexion PostgreSQL via variable d'environnement
db = PostgresqlDatabase(
    os.environ.get("POSTGRES_DB", "paiement"),
    user=os.environ.get("POSTGRES_USER", "admin"),
    password=os.environ.get("POSTGRES_PASSWORD", "admin"),
    host=os.environ.get("POSTGRES_HOST", "db"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
)

def initialize_db():
    from models import Product, Order
    db.connect(reuse_if_open=True)
    db.create_tables([Product, Order], safe=True)

def fetch_and_store_products():
    import requests
    from models import Product
    PRODUCTS_API_URL = "http://dimensweb.uqac.ca/~jgnault/shops/products/"
    response = requests.get(PRODUCTS_API_URL)
    if response.status_code == 200:
        for product in response.json().get("products", []):
            Product.get_or_create(
                id=product["id"],
                defaults={
                    "name": product["name"].replace('\x00', ''),
                    "description": product["description"].replace('\x00', ''),
                    "price": product["price"],
                    "weight": product["weight"],
                    "in_stock": product["in_stock"],
                    "image": product["image"].replace('\x00', ''),
                }
            )

        print(" Produits importés avec succès !")
    else:
        print(" Erreur lors de la récupération des produits :", response.status_code)
