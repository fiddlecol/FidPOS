document.addEventListener("DOMContentLoaded", () => {
  const addToCartBtn = document.getElementById("addToCartBtn");
  const cartBody = document.getElementById("cartBody");
  const cartTotalEl = document.getElementById("cartTotal");
  const checkoutBtn = document.getElementById("checkoutBtn");

  let cart = [];

  // ➕ Add to Cart
  addToCartBtn.addEventListener("click", async () => {
    const barcode = document.getElementById("scanInput").value.trim();
    const qty = parseInt(document.getElementById("scanQty").value);

    if (!barcode || qty <= 0) {
      alert("Enter a valid barcode and quantity!");
      return;
    }

    try {
      // 🔎 Fetch the item from backend
      const res = await fetch(`/items/lookup/${barcode}`);
      if (!res.ok) {
        alert("⚠️ Item not found in database!");
        return;
      }
      const item = await res.json();

      // ✅ Check if item already in cart
      const existing = cart.find(i => i.barcode === barcode);
      if (existing) {
        existing.qty += qty;
      } else {
        cart.push({
          barcode: item.barcode,
          name: item.name,
          price: parseFloat(item.price),
          qty
        });
      }

      renderCart();
    } catch (err) {
      console.error("❌ Error fetching item:", err);
      alert("❌ Failed to add item. Check console.");
    }
  });

  // 🧾 Checkout & Print
  checkoutBtn.addEventListener("click", async () => {
    if (cart.length === 0) {
      alert("🛑 Cart is empty!");
      return;
    }

    try {
      const res = await fetch("/items/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: cart })
      });

      const data = await res.json();
      if (res.ok) {
        // ✅ Open receipt in new window and print
        const receiptWindow = window.open("", "_blank");
        receiptWindow.document.write(data.receiptHtml);
        receiptWindow.document.close();
        receiptWindow.print();

        // Clear cart after checkout
        cart = [];
        renderCart();
      } else {
        alert("⚠️ " + (data.error || "Checkout failed"));
      }
    } catch (err) {
      console.error("❌ Checkout error:", err);
      alert("❌ Something went wrong. Check console.");
    }
  });

  // 🔁 Render Cart
  function renderCart() {
    cartBody.innerHTML = "";
    let total = 0;

    cart.forEach((item, index) => {
      const itemTotal = item.price * item.qty;
      total += itemTotal;

      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${item.barcode}</td>
        <td>${item.name}</td>
        <td>${item.price.toFixed(2)}</td>
        <td>${item.qty}</td>
        <td>${itemTotal.toFixed(2)}</td>
        <td><button class="btn btn-sm btn-danger remove-btn" data-index="${index}">🗑️</button></td>
      `;
      cartBody.appendChild(row);
    });

    cartTotalEl.textContent = total.toFixed(2);

    // Remove item from cart
    cartBody.querySelectorAll(".remove-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const idx = e.target.dataset.index;
        cart.splice(idx, 1);
        renderCart();
      });
    });
  }
});
