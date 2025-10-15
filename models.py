from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import pytz  # ✅ add this

db = SQLAlchemy()

EAT = pytz.timezone("Africa/Nairobi")  # ✅ proper tzinfo object

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(EAT))

    items = db.relationship("Item", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"

class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(EAT))

    def __repr__(self):
        return f"<Item {self.name} - {self.barcode}>"

class Sale(db.Model):
    __tablename__ = "sales"
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("sale_transactions.id"))
    barcode = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total = db.Column(db.Float, nullable=False)
    sold_at = db.Column(db.DateTime, default=lambda: datetime.now(EAT))

    def __repr__(self):
        return f"<Sale {self.item_name} x{self.quantity}>"


class SaleTransaction(db.Model):
    __tablename__ = "sale_transactions"
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, default=0)
    sold_at = db.Column(db.DateTime, default=lambda: datetime.now(EAT))

    # Relationship to Sale items
    items = db.relationship("Sale", backref="transaction", lazy=True)
    def __repr__(self):
        return f"<SaleTransaction {self.id} - Total: {self.total}>" 
    