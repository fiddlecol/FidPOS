# routes/categories.py
from flask import Blueprint, jsonify, request, render_template
from models import db, Category

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")

# 📄 Page render
@categories_bp.route("/")
def categories_page():
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template("categories.html", categories=categories)

# ➕ Add category
@categories_bp.route("/add", methods=["POST"])
def add_category():
    data = request.get_json() or request.form
    name = data.get("name")

    if not name:
        return jsonify({"error": "Category name is required"}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "Category already exists"}), 400

    cat = Category(name=name)
    db.session.add(cat)
    db.session.commit()

    return jsonify({"message": "Category added successfully", "id": cat.id, "name": cat.name})

# 🧾 Get all categories (API)
@categories_bp.route("/list", methods=["GET"])
def list_categories():
    cats = Category.query.order_by(Category.id.desc()).all()
    return jsonify([{"id": c.id, "name": c.name} for c in cats])

# ✏️ Update category
@categories_bp.route("/update/<int:id>", methods=["POST"])
def update_category(id):
    data = request.get_json() or request.form
    name = data.get("name")

    cat = Category.query.get(id)
    if not cat:
        return jsonify({"error": "Category not found"}), 404

    cat.name = name
    db.session.commit()
    return jsonify({"message": "Category updated successfully"})

# 🗑️ Delete category
@categories_bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_category(id):
    cat = Category.query.get(id)
    if not cat:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(cat)
    db.session.commit()
    return jsonify({"message": f"Category '{cat.name}' deleted"})
