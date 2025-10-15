document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("addItemForm");
  const itemsBody = document.getElementById("itemsBody");

  // 🔁 Fetch all items from backend
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
  form.addEventListener("submit", async (e) => {
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
  itemsBody.addEventListener("click", async (e) => {
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

  // ✏️ Edit item (inline update popup)
  itemsBody.addEventListener("click", async (e) => {
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

  // 🧠 Barcode scanning listener (focus auto-fill)
  const barcodeInput = document.getElementById("barcode");
  let barcodeBuffer = "";
  let scanTimeout;

  document.addEventListener("keypress", (e) => {
    if (e.target.tagName === "INPUT") return; // don't mess with typing

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

  // Initial load
  loadItems();
});

