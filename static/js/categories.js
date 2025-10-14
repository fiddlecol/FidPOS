document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("addCategoryForm");
  const body = document.getElementById("categoriesBody");

  async function loadCategories() {
    try {
      const res = await fetch("/categories/list");
      const data = await res.json();
      body.innerHTML = "";
      data.forEach((cat) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${cat.id}</td>
          <td>${cat.name}</td>
          <td>
            <button class="btn btn-sm btn-warning edit-btn" data-id="${cat.id}">✏️</button>
            <button class="btn btn-sm btn-danger delete-btn" data-id="${cat.id}">🗑️</button>
          </td>`;
        body.appendChild(row);
      });
    } catch (err) {
      console.error("❌ Failed to load categories:", err);
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value.trim();
    if (!name) return alert("Enter a category name!");

    const res = await fetch("/categories/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    const data = await res.json();
    if (res.ok) {
      alert("✅ " + data.message);
      form.reset();
      loadCategories();
    } else alert("⚠️ " + (data.error || "Failed to add"));
  });

  body.addEventListener("click", async (e) => {
    const id = e.target.dataset.id;
    if (e.target.classList.contains("delete-btn")) {
      if (!confirm("Delete this category?")) return;
      const res = await fetch(`/categories/delete/${id}`, { method: "DELETE" });
      const data = await res.json();
      if (res.ok) {
        alert("🗑️ " + data.message);
        loadCategories();
      } else alert("⚠️ " + (data.error || "Delete failed"));
    }

    if (e.target.classList.contains("edit-btn")) {
      const newName = prompt("Enter new category name:");
      if (!newName) return;
      const res = await fetch(`/categories/update/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName }),
      });
      const data = await res.json();
      if (res.ok) {
        alert("✅ " + data.message);
        loadCategories();
      } else alert("⚠️ " + (data.error || "Update failed"));
    }
  });

  loadCategories();
});
