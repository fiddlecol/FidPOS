from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Category, Item

products_bp = Blueprint("products", __name__, url_prefix="/products")


# 🧩 --- Category Routes ---
@products_bp.route("/categories", methods=["GET"])
def categories_page():
    categories = Category.query.order_by(Category.created_at.desc()).all()
    return render_template("categories.html", categories=categories)


@products_bp.route("/categories/add", methods=["POST"])
def add_category():
    name = request.form.get("name").strip()
    if not name:
        flash("Category name required!", "danger")
        return redirect(url_for("products.categories_page"))

    # check duplicate
    if Category.query.filter_by(name=name).first():
        flash("Category already exists!", "warning")
        return redirect(url_for("products.categories_page"))

    new_cat = Category(name=name)
    db.session.add(new_cat)
    db.session.commit()
    flash("✅ Category added successfully!", "success")
    return redirect(url_for("products.categories_page"))


@products_bp.route("/categories/delete/<int:category_id>", methods=["POST"])
def delete_category(category_id):
    cat = Category.query.get_or_404(category_id)
    db.session.delete(cat)
    db.session.commit()
    flash("🗑️ Category deleted.", "info")
    return redirect(url_for("products.categories_page"))


# 🧩 --- Item Routes ---
@products_bp.route("/items", methods=["GET"])
def items_page():
    items = Item.query.order_by(Item.created_at.desc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("items.html", items=items, categories=categories)


@products_bp.route("/items/add", methods=["POST"])
def add_item():
    name = request.form.get("name").strip()
    barcode = request.form.get("barcode").strip()
    price = request.form.get("price")
    quantity = request.form.get("quantity")
    category_id = request.form.get("category_id")

    if not all([name, barcode, price, quantity]):
        flash("All item fields are required!", "danger")
        return redirect(url_for("products.items_page"))

    # duplicate barcode check
    if Item.query.filter_by(barcode=barcode).first():
        flash("Item with that barcode already exists!", "warning")
        return redirect(url_for("products.items_page"))

    item = Item(
        name=name,
        barcode=barcode,
        price=float(price),
        quantity=int(quantity),
        category_id=int(category_id) if category_id else None,
    )

    db.session.add(item)
    db.session.commit()
    flash("✅ Item added successfully!", "success")
    return redirect(url_for("products.items_page"))


@products_bp.route("/items/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("🗑️ Item deleted.", "info")
    return redirect(url_for("products.items_page"))


# 🧩 --- API Routes (for AJAX/Scanner use) ---
@products_bp.route("/api/items", methods=["GET"])
def api_get_items():
    items = Item.query.all()
    data = [
        {
            "id": i.id,
            "barcode": i.barcode,
            "name": i.name,
            "price": i.price,
            "quantity": i.quantity,
            "category": i.category.name if i.category else None,
        }
        for i in items
    ]
    return jsonify(data)


@products_bp.route("/api/items/<barcode>", methods=["GET"])
def api_get_item_by_barcode(barcode):
    item = Item.query.filter_by(barcode=barcode).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(
        {
            "id": item.id,
            "barcode": item.barcode,
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity,
            "category": item.category.name if item.category else None,
        }
    )
