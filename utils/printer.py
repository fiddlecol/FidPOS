import datetime
import os
import traceback

# Try importing only stable classes first
try:
    from escpos.printer import Usb, Network  # Bluetooth left out
except Exception:
    Usb = None
    Network = None


def _get_bluetooth_printer_class():
    """Try loading Bluetooth class only if available."""
    try:
        from escpos.printer import Bluetooth  # imported lazily
        return Bluetooth
    except Exception:
        return None


def format_receipt_text(sale, shop_name="FidPOS", shop_address=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"{shop_name}".center(32),
        f"{shop_address}".center(32) if shop_address else "",
        "-" * 32,
        f"Item: {sale.item_name}",
        f"Barcode: {sale.barcode}",
        f"Qty: {sale.quantity}  x  {sale.price:.2f}",
        "-" * 32,
        f"Total: KSh {sale.total:.2f}",
        "-" * 32,
        f"Date: {timestamp}",
        "Thank you for shopping!",
        "",
        "Powered by FidPOS"
    ]
    return "\n".join([l for l in lines if l])


def print_receipt(
    sale,
    shop_name="FidPOS",
    shop_address="",
    mode="network",
    usb_vid=None,
    usb_pid=None,
    bt_mac=None,
    network_ip=None,
    network_port=9100,
):
    text = format_receipt_text(sale, shop_name, shop_address)
    print(f"[printer] Printing mode: {mode}")

    def _save_fallback():
        os.makedirs("receipts", exist_ok=True)
        fname = os.path.join(
            "receipts", f"receipt_{sale.id}_{int(datetime.datetime.now().timestamp())}.txt"
        )
        with open(fname, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[printer] Saved receipt to {fname}")
        return False

    try:
        if mode == "usb" and Usb:
            try:
                p = Usb(int(usb_vid, 16), int(usb_pid, 16))
                p.text(text + "\n")
                p.cut()
                print("[printer] USB print done.")
                return True
            except Exception as e:
                print("[printer] USB print failed:", e)
                traceback.print_exc()
                return _save_fallback()

        elif mode == "network" and Network and network_ip:
            try:
                p = Network(network_ip, port=network_port)
                p.text(text + "\n")
                p.cut()
                print("[printer] Network print done.")
                return True
            except Exception as e:
                print("[printer] Network print failed:", e)
                traceback.print_exc()
                return _save_fallback()

        elif mode == "bluetooth":
            Bluetooth = _get_bluetooth_printer_class()
            if not Bluetooth:
                print("[printer] Bluetooth not supported on this device.")
                return _save_fallback()
            try:
                p = Bluetooth(bt_mac)
                p.text(text + "\n")
                p.cut()
                print("[printer] Bluetooth print done.")
                return True
            except Exception as e:
                print("[printer] Bluetooth print failed:", e)
                traceback.print_exc()
                return _save_fallback()

        else:
            print("[printer] Unsupported mode — saving to file.")
            return _save_fallback()

    except Exception as e:
        print("[printer] Unexpected error:", e)
        traceback.print_exc()
        return _save_fallback()

def initialize_printer():
    """
    Initialize printer connection — currently mocked for systems without Bluetooth/USB.
    Replace with real printer setup when hardware is available.
    """
    print("🖨️ Printer initialization skipped (no adapter detected).")

def print_receipt(sale_data):
    """
    Mock print function — would normally send receipt data to printer.
    """
    print("🧾 Mock printing receipt:")
    for key, value in sale_data.items():
        print(f"  {key}: {value}")
    print("✅ Receipt printed (mock).")