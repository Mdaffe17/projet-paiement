#  Projet Paiement - API Flask
[NOM] : [DAFFE] 
[PRENOM]: [MOUCTAR] 
[CODE PERMANENT]: [DAFM01119900]

##  Description
Ce projet est une API REST permettant la gestion des commandes en ligne.  
L'application permet de :
- Récupérer la liste des produits disponibles
- Créer une commande pour un produit
- Ajouter les informations du client (adresse & email)
- Calculer les taxes et les frais de livraison 
- Effectuer un paiement avec carte de crédit 

---

##  Installation et Exécution
pip install -r requirements.txt
###  **Installation des dépendances**
Avant de commencer, assurez-vous d'avoir au minimum **Python 3.6+** installé sur votre machine.

####  Installer les bibliothèques nécessaires :

##  **Démarrer l'application Flask**
python app.py
## 1. Récupérer la liste des produits
curl -X GET http://127.0.0.1:5000/products
## 2. Créer une commande
curl -X POST http://127.0.0.1:5000/orders \
     -H "Content-Type: application/json" \
     -d '{"product": {"id": 1, "quantity": 2}}'
## 3. Ajouter l'adresse d'expédition et l'email du client
curl -X PUT http://127.0.0.1:5000/orders/1 \
     -H "Content-Type: application/json" \
     -d '{
          "email": "client@example.com",
          "shipping_information": {
              "country": "Canada",
              "address": "201, rue Président-Kennedy",
              "postal_code": "G7X 3Y7",
              "city": "Chicoutimi",
              "province": "QC"
          }
     }'
## 4. Effectuer un paiement
curl -X PUT http://127.0.0.1:5000/orders/1 \
     -H "Content-Type: application/json" \
     -d '{
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2024,
            "expiration_month": 9,
            "cvv": "123"
        }
     }'
## 5. Lancer les tests
pytest tests/ -v
