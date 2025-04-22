import sys
import os

sys.path.insert(0, "/Users/mouctardaffe/Desktop/projet_paiement")

import pytest
from app import app  #  Flask App
from database import initialize_db, db
from models import Order, Product


@pytest.fixture
def client():
    """Créer un client de test Flask avec une base de données propre."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["DEBUG"] = False

    with app.test_client() as client:
        with app.app_context():
            initialize_db()
        yield client  # Retourne le client de test

        #  Fermer proprement la base après les tests
        if not db.is_closed():
            db.close()


def test_db_connection():
    """Vérifie si la base de données est accessible sans ouvrir plusieurs connexions."""
    assert not db.is_closed(), "La base de données devrait être ouverte"
    db.close()  # Fermer après vérification
    assert db.is_closed(), "La base de données devrait être fermée après fermeture"


#  Test 1 : Vérifier que la liste des produits est retournée
def test_get_products(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert "products" in response.json

#  Test 2 : Vérifier de la création d'une commande valide
def test_create_order(client):
    data = {"product": {"id": 1, "quantity": 2}}
    response = client.post("/orders", json=data)
    assert response.status_code == 302  # Redirection après création
    assert "order_id" in response.json

#  Test 3 : Vérifier qu'une commande invalide est rejetée (quantité négative)
def test_create_order_invalid(client):
    data = {"product": {"id": 1, "quantity": -1}}
    response = client.post("/orders", json=data)
    assert response.status_code == 422  # Erreur Unprocessable Entity

#  Test 4 : Vérifier de la mise à jour d'une commande avec une adresse et email
def test_update_order(client):
    order = Order.create(product=Product.get(Product.id == 1), quantity=2, total_price=56.2)
    data = {
        "email": "test@example.com",
        "shipping_information": {
            "country": "Canada",
            "address": "201, rue Président-Kennedy",
            "postal_code": "G7X 3Y7",
            "city": "Chicoutimi",
            "province": "QC"
        }
    }
    response = client.put(f"/orders/{order.id}", json=data)
    assert response.status_code == 200
    assert response.json["order"]["email"] == "test@example.com"

#  Test 5 : Vérifier le paiement d'une commande
def test_pay_order(client):
    order = Order.create(product=Product.get(Product.id == 1), quantity=2, total_price=56.2)
    data = {
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2024,
            "expiration_month": 9,
            "cvv": "123"
        }
    }
    response = client.put(f"/orders/{order.id}", json=data)
    assert response.status_code in [200, 422]  # Paiement accepté ou refusé
