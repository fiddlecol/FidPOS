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
  async function payWithMpesa(saleId) {
    try {
      const res = await fetch("/sales/pay", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sale_id: saleId, phone: "254XXXXXXXXX" }),
      });
      const data = await res.json();
      if (res.ok) alert("✅ STK Push sent. Approve payment on phone.");
      else alert("⚠️ " + (data.error || "Payment request failed."));
    } catch (err) {
      console.error("❌ Payment error:", err);
    }
  }

  function payInCash(saleId) {
    alert(`💵 Sale #${saleId} marked as cash payment.`);
    // optional: send to backend `/sales/cash`
  }

  // 📲 M-Pesa button
  mpesaBtn?.addEventListener("click", () => {
    if (!currentSaleId) return alert("⚠️ No active sale.");
    paymentMethod = "mpesa";
    payWithMpesa(currentSaleId);
  });

  // 💵 Cash button
  cashBtn?.addEventListener("click", () => {
    if (!currentSaleId) return alert("⚠️ No active sale.");
    paymentMethod = "cash";
    payInCash(currentSaleId);
  });

  // 🧾 Checkout
  checkoutBtn?.addEventListener("click", () => {
    if (!paymentMethod) return alert("⚠️ Choose payment method first.");
    alert(`🧾 Checkout complete. Payment: ${paymentMethod.toUpperCase()}`);
    // optional: print receipt here
  });

  // Initial load
  loadItems();
});
