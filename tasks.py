import os
import requests
from playhouse.db_url import connect
from models import Order

# Connexion à la base de données via l'URL d'environnement
db = connect(os.environ.get("DATABASE_URL", "postgres://admin:admin@db:5432/paiement"))
db.connect(reuse_if_open=True)

# Simulation de paiement activée ?
simulate = os.getenv("SIMULATE_PAYMENT", "true").lower() == "true"

# URL de l’API de paiement externe
PAYMENT_API_URL = "http://dimensweb.uqac.ca/~jgnault/shops/pay/"

def process_payment(order_id, credit_card):
    """Tâche exécutée en arrière-plan pour traiter le paiement."""
    order = Order.get_or_none(Order.id == order_id)
    if not order or order.paid:
        print(f" Paiement refusé - commande {order_id} introuvable ou déjà payée.")
        return

    if not order.email or not order.address:
        print(f" Commande {order_id} incomplète. Email ou adresse manquant.")
        return

    if simulate:
        print(f" [SIMULATION] Paiement réussi pour commande {order_id}")
        order.paid = True
        order.transaction_id = "SIMULATED-123456"
        order.save()
        return

    # Données pour l'API réelle
    payment_data = {
        "credit_card": {
            "name": credit_card["name"],
            "number": credit_card["number"],
            "expiration_year": int(credit_card["expiration_year"]),
            "expiration_month": int(credit_card["expiration_month"]),
            "cvv": str(credit_card["cvv"])
        },
        "amount_charged": int(order.total_price + order.tax + order.shipping_cost)
    }

    try:
        print(f" Paiement en cours pour commande {order_id}...")
        response = requests.post(PAYMENT_API_URL, json=payment_data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            transaction = result.get("transaction", {})
            if transaction.get("success"):
                order.paid = True
                order.transaction_id = transaction.get("id")
                order.save()
                print(f" Paiement réussi pour commande {order_id}")
            else:
                print(f" Paiement échoué : {result}")
        else:
            print(f" Erreur API paiement : {response.status_code} - {response.text}")

    except requests.RequestException as e:
        print(f" Erreur de communication avec l’API de paiement : {str(e)}")
