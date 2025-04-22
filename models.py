from peewee import *
from database import db

class BaseModel(Model):
    class Meta:
        database = db

class Product(BaseModel):
    id = AutoField()
    name = CharField()
    description = TextField()
    price = FloatField()
    weight = IntegerField()
    in_stock = BooleanField(default=True)
    image = CharField(null=True)

class Order(BaseModel):
    id = AutoField()
    product = ForeignKeyField(Product, backref="orders")
    quantity = IntegerField()
    total_price = FloatField()
    paid = BooleanField(default=False)
    transaction_id = CharField(null=True)
    email = CharField()
    address = CharField()
    province = CharField()
    tax = FloatField(null=True)
    shipping_cost = FloatField(null=True)
