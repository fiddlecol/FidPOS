# routes/sales.py
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from models import db, Item, Sale, SaleTransaction
from datetime import datetime, timedelta
from pytz import timezone

EAT = timezone("Africa/Nairobi")

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")

# 🧾 POS main page
@sales_bp.route("/", methods=["GET"])
def pos_page():
    items = Item.query.all()
    return render_template("pos.html", items=items)

from utils.printer import print_receipt

# 🛒 Add item to sale (scan or manual)
@sales_bp.route("/add", methods=["POST"])
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
@sales_bp.route("/receipt/<int:sale_id>")
def receipt(sale_id):
    transaction = SaleTransaction.query.get_or_404(sale_id)
    shop_name = "FidPOS Store"

    return render_template(
        "receipt.html",
        items=transaction.items,
        total=transaction.total,
        shop_name=shop_name,
        date=transaction.sold_at
    )



# 📊 All sales (for report or testing)
@sales_bp.route("/all", methods=["GET"])
def all_sales():
    sales = Sale.query.order_by(Sale.sold_at.desc()).all()
    return render_template("reports.html", sales=sales)


@sales_bp.route("/data", methods=["GET"])
def sales_data():
    start_date_str = request.args.get("startDate")
    end_date_str = request.args.get("endDate")

    query = Sale.query

    if start_date_str:
        try:
            start_date = EAT.localize(datetime.strptime(start_date_str, "%Y-%m-%d"))
            query = query.filter(Sale.sold_at >= start_date)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date = EAT.localize(datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1))
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

# 🧾 Checkout (finalize sale, clear cart)
@sales_bp.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json()
    items = data.get("items", [])

    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    # Create one transaction
    transaction = SaleTransaction()
    db.session.add(transaction)
    db.session.flush()  # get transaction.id before commit

    total_sum = 0

    for item in items:
        price = float(item.get("price", 0))
        qty = int(item.get("qty", 1))
        total = price * qty
        total_sum += total

        sale = Sale(
            transaction_id=transaction.id,
            barcode=item.get("barcode", ""),
            item_name=item.get("name", ""),
            price=price,
            quantity=qty,
            total=total
        )
        db.session.add(sale)

        # ✅ Deduct stock
        barcode = item.get("barcode")
        db_item = Item.query.filter_by(barcode=barcode).first()
        if db_item:
            if db_item.quantity < qty:
                return jsonify({"error": f"Not enough stock for {db_item.name}"}), 400
            db_item.quantity = max(0, db_item.quantity - qty)

    transaction.total = total_sum
    db.session.commit()

    return jsonify({"sale_id": transaction.id})

# Mpesa payment integration
from .mpesa import lipa_na_mpesa
from models import SaleTransaction
from flask import current_app
import uuid

@sales_bp.route("/pay", methods=["POST"])
def pay_with_mpesa():
    data = request.get_json()
    phone = data.get("phone")
    sale_id = data.get("sale_id")

    if not (phone and sale_id):
        return jsonify({"error": "Missing phone or sale_id"}), 400

    transaction = SaleTransaction.query.get(sale_id)
    if not transaction:
        return jsonify({"error": "Invalid sale"}), 404

    amount = float(transaction.total)
    callback_url = f"{request.host_url}mpesa/mpesa/callback"
    account_ref = f"FIDPOS-{sale_id}-{uuid.uuid4().hex[:6]}"

    resp = lipa_na_mpesa(phone, amount, account_ref, callback_url)
    return jsonify(resp)

