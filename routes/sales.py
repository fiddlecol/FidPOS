# routes/sales.py
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from models import db, Item, Sale
from datetime import datetime

bp = Blueprint("sales", __name__, url_prefix="/sales")

# 🧾 POS main page
@bp.route("/", methods=["GET"])
def pos_page():
    items = Item.query.all()
    return render_template("pos.html", items=items)

from utils.printer import print_receipt

# 🛒 Add item to sale (scan or manual)
@bp.route("/add", methods=["POST"])
def add_sale():
    data = request.get_json() or request.form
    barcode = data.get("barcode")
    quantity = int(data.get("quantity", 1))

    item = Item.query.filter_by(barcode=barcode).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404

    if item.quantity < quantity:
        return jsonify({"error": "Not enough stock"}), 400

    total = item.price * quantity
    sale = Sale(
        barcode=item.barcode,
        item_name=item.name,
        price=item.price,
        quantity=quantity,
        total=total
    )

    # Deduct from stock
    item.quantity -= quantity
    db.session.add(sale)
    db.session.commit()

    # 🖨️ Print receipt automatically
    try:
        print_receipt(
            sale,
            shop_name="FidPOS Store",  # You can set this dynamically later
            mode="bluetooth"           # or "usb" / "network" depending on printer
        )
    except Exception as e:
        print(f"[⚠️ Printer Failed] {e}")

    return jsonify({
        "message": "Sale recorded successfully",
        "item": {
            "barcode": item.barcode,
            "name": item.name,
            "price": item.price,
            "quantity": quantity,
            "total": total
        }
    })


# 🧾 Generate receipt (renders HTML receipt page)
@bp.route("/receipt/<int:sale_id>")
def receipt(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    shop_name = "Kitere Beauty Shop"
    return render_template("receipt.html", sale=sale, shop_name=shop_name, date=datetime.now())

# 📊 All sales (for report or testing)
@bp.route("/all", methods=["GET"])
def all_sales():
    sales = Sale.query.order_by(Sale.sold_at.desc()).all()
    return render_template("reports.html", sales=sales)


@bp.route("/data", methods=["GET"])
def sales_data():
    start_date_str = request.args.get("startDate")
    end_date_str = request.args.get("endDate")

    query = Sale.query

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            query = query.filter(Sale.sold_at >= start_date)
        except ValueError:
            pass

    if end_date_str:
        try:
            # Add 1 day so the end date is inclusive
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Sale.sold_at < end_date)
        except ValueError:
            pass

    sales = query.order_by(Sale.sold_at.desc()).all()

    data = [
        {
            "id": s.id,
            "item": s.item_name,
            "total": float(s.total),
            "date": s.sold_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for s in sales
    ]
    return jsonify(data), 200

