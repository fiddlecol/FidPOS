document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("addItemForm");
  const itemsBody = document.getElementById("itemsBody");
  const barcodeInput = document.getElementById("barcode");
  const mpesaBtn = document.getElementById("mpesaBtn");
  const cashBtn = document.getElementById("cashBtn");
  const checkoutBtn = document.getElementById("checkoutBtn");

  let currentSaleId = null; // dynamically set when a sale starts
  let paymentMethod = null; // "mpesa" or "cash"

  // 🔁 Load all items
  async function loadItems() {
    try {
      const res = await fetch("/items/");
      const data = await res.json();

      itemsBody.innerHTML = "";
      data.forEach((item) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${item.barcode}</td>
          <td>${item.name}</td>
          <td>${item.category}</td>
          <td>${item.price}</td>
          <td>${item.quantity}</td>
          <td>
            <button class="btn btn-sm btn-warning edit-btn" data-id="${item.id}">✏️</button>
            <button class="btn btn-sm btn-danger delete-btn" data-id="${item.id}">🗑️</button>
          </td>
        `;
        itemsBody.appendChild(row);
      });
    } catch (err) {
      console.error("❌ Failed to load items:", err);
    }
  }

  // ➕ Add item
  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const jsonData = Object.fromEntries(formData.entries());

    try {
      const res = await fetch("/items/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(jsonData),
      });
      const data = await res.json();

      if (res.ok) {
        alert("✅ Item added successfully!");
        form.reset();
        loadItems();
      } else {
        alert("⚠️ " + (data.error || "Failed to add item."));
      }
    } catch (err) {
      console.error("❌ Error adding item:", err);
    }
  });

  // 🗑️ Delete item
  itemsBody?.addEventListener("click", async (e) => {
    if (e.target.classList.contains("delete-btn")) {
      const id = e.target.dataset.id;
      if (!confirm("Delete this item?")) return;

      try {
        const res = await fetch(`/items/delete/${id}`, { method: "DELETE" });
        const data = await res.json();
        if (res.ok) {
          alert("🗑️ " + data.message);
          loadItems();
        } else {
          alert("⚠️ " + (data.error || "Failed to delete."));
        }
      } catch (err) {
        console.error("❌ Delete failed:", err);
      }
    }
  });

  // ✏️ Edit item
  itemsBody?.addEventListener("click", async (e) => {
    if (e.target.classList.contains("edit-btn")) {
      const id = e.target.dataset.id;
      const name = prompt("Enter new name:");
      const price = prompt("Enter new price:");
      const quantity = prompt("Enter new quantity:");
      if (!name || !price || !quantity) return;

      try {
        const res = await fetch(`/items/update/${id}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, price, quantity }),
        });
        const data = await res.json();

        if (res.ok) {
          alert("✅ " + data.message);
          loadItems();
        } else {
          alert("⚠️ " + (data.error || "Update failed."));
        }
      } catch (err) {
        console.error("❌ Update error:", err);
      }
    }
  });

  // 🧠 Barcode scanning listener
  let barcodeBuffer = "";
  let scanTimeout;
  document.addEventListener("keypress", (e) => {
    if (e.target.tagName === "INPUT") return;
    barcodeBuffer += e.key;
    clearTimeout(scanTimeout);
    scanTimeout = setTimeout(() => {
      if (barcodeBuffer.length >= 6) {
        barcodeInput.value = barcodeBuffer.trim();
        barcodeInput.focus();
      }
      barcodeBuffer = "";
    }, 200);
  });

// 💰 Payment handlers
async function payWithMpesa(saleId, phone) {
  try {
    const res = await fetch("/sales/pay", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sale_id: saleId, phone }),
    });
    const data = await res.json();
    if (res.ok) {
      alert("✅ STK Push sent. Approve payment on your phone.");
      pollPaymentStatus(saleId);
    } else {
      alert("⚠️ " + (data.error || "Payment request failed."));
    }
  } catch (err) {
    console.error("❌ Payment error:", err);
  }
}

// 🔁 Poll M-Pesa payment status
async function pollPaymentStatus(saleId) {
  const interval = setInterval(async () => {
    const res = await fetch(`/sales/status/${saleId}`);
    const data = await res.json();

    if (data.status === "Success") {
      clearInterval(interval);
      alert("✅ M-Pesa payment confirmed!");
      finalizeCheckout(saleId, "mpesa");
    } else if (data.status === "Failed") {
      clearInterval(interval);
      alert("❌ Payment failed or cancelled.");
    }
  }, 3000);
}

// 💵 Cash payment — auto checkout immediately
async function payInCash(saleId) {
  try {
    const res = await fetch("/sales/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sale_id: saleId, payment_method: "cash" }),
    });
    const data = await res.json();

    if (res.ok) {
      alert("💵 Sale completed with cash.");
      window.open(`/sales/receipt/${data.sale_id}`, "_blank");
    } else {
      alert("⚠️ Checkout failed: " + (data.error || "unknown error"));
    }
  } catch (err) {
    console.error("❌ Cash checkout error:", err);
  }
}

// 🧾 Shared finalize function
async function finalizeCheckout(saleId, method) {
  try {
    const res = await fetch("/sales/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sale_id: saleId, payment_method: method }),
    });
    const data = await res.json();

    if (res.ok) {
      window.open(`/sales/receipt/${data.sale_id}`, "_blank");
    } else {
      alert("⚠️ Checkout failed: " + (data.error || "unknown error"));
    }
  } catch (err) {
    console.error("❌ Checkout error:", err);
  }
}

// 📲 M-Pesa button — popup with locked 254 prefix
mpesaBtn?.addEventListener("click", () => {
  if (!currentSaleId) return alert("⚠️ No active sale.");
  paymentMethod = "mpesa";

  // Build popup
  const popup = document.createElement("div");
  popup.innerHTML = `
    <div id="mpesaPopup" style="
      position: fixed; inset: 0;
      background: rgba(0,0,0,0.6);
      display: flex; align-items: center; justify-content: center;
      z-index: 9999;">
      <div style="
        background: #fff; padding: 20px;
        border-radius: 12px; width: 320px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        text-align: center;">
        <h5>📱 Enter M-Pesa Number</h5>
        <div style="display:flex; align-items:center; margin-top:12px;">
          <span style="
            background:#f0f0f0; padding:10px;
            border:1px solid #ccc;
            border-radius:5px 0 0 5px;
            font-weight:bold;">254</span>
          <input type="text" id="mpesaPhone"
            placeholder="7XXXXXXXX or 1XXXXXXXX"
            style="flex:1; padding:10px;
            border:1px solid #ccc;
            border-left:0; border-radius:0 5px 5px 0;
            font-size:16px;" maxlength="9">
        </div>
        <div style="margin-top:18px;">
          <button id="confirmMpesaBtn" class="btn btn-success" style="margin-right:8px;">✅ Confirm</button>
          <button id="cancelMpesaBtn" class="btn btn-danger">❌ Cancel</button>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(popup);

  const confirmBtn = popup.querySelector("#confirmMpesaBtn");
  const cancelBtn = popup.querySelector("#cancelMpesaBtn");
  const phoneInput = popup.querySelector("#mpesaPhone");

  // Cancel
  cancelBtn.addEventListener("click", () => popup.remove());

  // Confirm
  confirmBtn.addEventListener("click", () => {
    const suffix = phoneInput.value.trim();
    const fullPhone = `254${suffix}`;
    const pattern = /^254(7|1)\d{8}$/;

    if (!pattern.test(fullPhone)) {
      alert("❌ Invalid number. Use 2547XXXXXXXX or 2541XXXXXXXX");
      return;
    }

    confirmBtn.disabled = true;
    confirmBtn.innerText = "⏳ Sending STK...";
    payWithMpesa(currentSaleId, fullPhone);
    setTimeout(() => popup.remove(), 800);
  });
});

// 💵 Cash button — instant checkout
cashBtn?.addEventListener("click", () => {
  if (!currentSaleId) return alert("⚠️ No active sale.");
  paymentMethod = "cash";
  payInCash(currentSaleId);
});

// 🧾 Checkout button (manual fallback)
checkoutBtn?.addEventListener("click", () => {
  if (!paymentMethod) return alert("⚠️ Choose payment method first.");
  finalizeCheckout(currentSaleId, paymentMethod);
});

  // Initial load
  loadItems();
});
