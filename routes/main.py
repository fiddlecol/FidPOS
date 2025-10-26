# routes/main.py
from flask import Blueprint, render_template
from models import Category, Item, Sale

main_bp = Blueprint("main", __name__)

# 🏠 Home / Dashboard
@main_bp.route("/")
def index():
    total_items = Item.query.count()
    total_sales = Sale.query.count()
    total_stock = sum(item.quantity for item in Item.query.all())
    total_revenue = sum(sale.total for sale in Sale.query.all())

    return render_template(
        "index.html",
        total_items=total_items,
        total_sales=total_sales,
        total_stock=total_stock,
        total_revenue=total_revenue
    )

# 🧴 Categories page
@main_bp.route("/categories")
def categories_page():
    categories = Category.query.order_by(Category.name).all()
    return render_template("categories.html", categories=categories)

# 📦 Items page
@main_bp.route("/items")
def items_page():
    categories = Category.query.order_by(Category.name).all()
    return render_template("items.html", categories=categories)

# 💰 POS page (sales)
@main_bp.route("/pos")
def pos_page():
    return render_template("pos.html")

# 📑 Reports page
@main_bp.route("/reports")
def reports_page():
    sales = Sale.query.order_by(Sale.sold_at.desc()).all()
    return render_template("reports.html", sales=sales)
# ⚙️ Settings page
@main_bp.route("/settings")
def settings_page():
    return render_template("settings.html") 