import os
import json
import redis
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from peewee import DoesNotExist
from models import Product, Order
from rq import Queue
from playhouse.shortcuts import model_to_dict
import tasks

routes_bp = Blueprint("routes", __name__)

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
r = redis.from_url(redis_url)
task_queue = Queue("paiement-tasks", connection=r)

@routes_bp.route("/")
def home():
    products = Product.select()
    return render_template("index.html", products=products)

@routes_bp.route("/order/<int:product_id>")
def order_page(product_id):
    try:
        product = Product.get(Product.id == product_id)
    except DoesNotExist:
        return "Produit introuvable", 404

    order = Order.select().where(Order.product == product, Order.paid == False).order_by(Order.id.desc()).first()
    return render_template("order.html", product=product, order=order)

@routes_bp.route("/order", methods=["POST"])
def submit_order_form():
    try:
        product_id = int(request.form["product_id"])
        quantity = int(request.form["quantity"])
        email = request.form["email"]
        address = request.form["address"]
        province = request.form["province"]
    except (KeyError, ValueError):
        return "Champs invalides", 400

    try:
        product = Product.get(Product.id == product_id)
        total_price = product.price * quantity
        tax_rates = {"QC": 0.14975, "ON": 0.13, "AB": 0.05, "BC": 0.12, "NS": 0.15}
        tax = total_price * tax_rates.get(province, 0)
        weight = product.weight * quantity
        shipping = 5.0 if weight < 500 else 10.0 if weight < 2000 else 25.0

        order = Order.create(
            product=product,
            quantity=quantity,
            total_price=total_price,
            email=email,
            address=address,
            province=province,
            tax=tax,
            shipping_cost=shipping
        )
        return redirect(url_for("routes.order_status", order_id=order.id))
    except DoesNotExist:
        return "Produit non trouvé", 404

@routes_bp.route("/order/<int:order_id>/payment", methods=["GET", "POST"])
def payment_form(order_id):
    order = Order.get_or_none(Order.id == order_id)
    if not order:
        return "Commande introuvable", 404

    if request.method == "POST":
        credit_card = {
            "name": request.form["name"],
            "number": request.form["number"],
            "expiration_month": request.form["expiration_month"],
            "expiration_year": request.form["expiration_year"],
            "cvv": request.form["cvv"]
        }
        job = task_queue.enqueue(tasks.process_payment, order_id, credit_card)
        return redirect(url_for("routes.order_status", order_id=order.id, message="paiement"))

    return render_template("payment.html", order=order)

@routes_bp.route("/order/<int:order_id>/status")
def order_status(order_id):
    order = Order.get_or_none(Order.id == order_id)
    if not order:
        return "Commande introuvable", 404

    message = request.args.get("message")
    return render_template("status_order.html", order=order, message=message)
@routes_bp.route("/order/check")
def order_check_form():
    return render_template("order_check.html")

@routes_bp.route("/order/check", methods=["POST"])
def order_check_redirect():
    try:
        order_id = int(request.form["order_id"])
        return redirect(url_for("routes.order_status", order_id=order_id))
    except ValueError:
        return "ID invalide", 400
