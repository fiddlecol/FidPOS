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
    const res = await fetch("/sales/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: cart })
    });

    const data = await res.json();

    if (res.ok) {
      // ✅ If backend returns multiple sale IDs (for grouped receipts)
      if (data.sale_ids && Array.isArray(data.sale_ids)) {
        const saleIds = data.sale_ids.join(",");
        window.open(`/sales/receipt/multi?ids=${saleIds}`, "_blank");
      } 
      // ✅ Single sale receipt
      else if (data.sale_id) {
        window.open(`/sales/receipt/${data.sale_id}`, "_blank");
      } 
      else {
        alert("⚠️ Checkout succeeded but no receipt ID returned!");
      }

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

    // 💸 M-Pesa Payment Flow
  const mpesaBtn = document.getElementById("mpesaBtn");
  const mpesaPhoneContainer = document.getElementById("mpesaPhoneContainer");
  const confirmMpesaBtn = document.getElementById("confirmMpesaBtn");

  // Step 1: show phone input when M-Pesa button clicked
  mpesaBtn.addEventListener("click", () => {
    mpesaBtn.style.display = "none";
    mpesaPhoneContainer.style.display = "block";
  });

  // Step 2: confirm payment (STK push)
  confirmMpesaBtn.addEventListener("click", async () => {
    const phone = document.getElementById("mpesaPhone").value.trim();
    if (!phone.match(/^2547\d{8}$/)) {
      alert("⚠️ Enter valid M-Pesa number (e.g. 254712345678)");
      return;
    }

    if (cart.length === 0) {
      alert("🛒 Cart is empty!");
      return;
    }

    const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
    confirmMpesaBtn.disabled = true;
    confirmMpesaBtn.innerText = "⏳ Sending STK Push...";

    try {
      // call backend to send STK push
      const r = await fetch("/mpesa/stkpush", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone, amount: total, items: cart }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error || "STK Push failed");

      pollPaymentStatus(data.CheckoutRequestID);
    } catch (err) {
      alert("💥 Error: " + err.message);
      confirmMpesaBtn.disabled = false;
      confirmMpesaBtn.innerText = "✅ Confirm & Send STK Push";
    }
  });

  // Step 3: poll backend for payment status
  async function pollPaymentStatus(checkoutID) {
    const interval = setInterval(async () => {
      const res = await fetch(`/api/mpesa/status?checkoutRequestID=${checkoutID}`);
      const data = await res.json();

      if (data.status === "Success") {
        clearInterval(interval);
        alert("✅ Payment successful!");
        finalizeCheckout(data);
      } else if (data.status === "Failed") {
        clearInterval(interval);
        alert("❌ Payment failed or cancelled.");
        resetPaymentUI();
      }
    }, 3000);
  }

  // Step 4: finalize checkout & print receipt
  async function finalizeCheckout(paymentData) {
    try {
      const res = await fetch("/sales/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: cart, payment: paymentData }),
      });
      const data = await res.json();

      if (res.ok) {
        // handle both single and multi receipt IDs like before
        if (data.sale_ids && Array.isArray(data.sale_ids)) {
          const ids = data.sale_ids.join(",");
          window.open(`/sales/receipt/multi?ids=${ids}`, "_blank");
        } else if (data.sale_id) {
          window.open(`/sales/receipt/${data.sale_id}`, "_blank");
        } else {
          alert("⚠️ Checkout succeeded but no receipt ID returned!");
        }

        cart = [];
        renderCart();
      } else {
        alert("⚠️ Checkout failed: " + (data.error || "unknown error"));
      }
    } catch (err) {
      alert("💥 Error during checkout: " + err.message);
    } finally {
      resetPaymentUI();
    }
  }

  // Step 5: reset UI if payment fails or ends
  function resetPaymentUI() {
    confirmMpesaBtn.disabled = false;
    confirmMpesaBtn.innerText = "✅ Confirm & Send STK Push";
    mpesaBtn.style.display = "block";
    mpesaPhoneContainer.style.display = "none";
  }
});
