document.addEventListener("DOMContentLoaded", () => {
  const filterBtn = document.getElementById("filterBtn");
  const tableBody = document.getElementById("salesBody");
  const canvas = document.getElementById("salesChart");
  let salesChart = null;

  async function loadReports() {
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;

    const params = new URLSearchParams();
    if (startDate) params.append("startDate", startDate);
    if (endDate) params.append("endDate", endDate);

    try {
      const res = await fetch(`/sales/data?${params.toString()}`);
      const data = await res.json();

      // Clear table
      tableBody.innerHTML = "";

      // Clear previous chart completely
      if (salesChart) {
        salesChart.destroy();
        salesChart = null;
      }

      if (!data || data.length === 0) {
        tableBody.innerHTML = `
          <tr>
            <td colspan="4" class="text-center text-muted">No sales found for this period.</td>
          </tr>
        `;
        // Clear canvas for chart
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        return;
      }

      const labels = [];
      const totals = [];

      data.forEach(sale => {
        labels.push(sale.item);
        totals.push(sale.total);

        const row = `
          <tr>
            <td>${sale.id}</td>
            <td>${sale.item}</td>
            <td>${sale.total.toLocaleString()}</td>
            <td>${sale.date}</td>
          </tr>
        `;
        tableBody.insertAdjacentHTML("beforeend", row);
      });

      // Recreate chart
      salesChart = new Chart(canvas.getContext("2d"), {
        type: "bar",
        data: {
          labels: labels,
          datasets: [{
            label: "Total Sales (KSh)",
            data: totals,
            backgroundColor: "rgba(54, 162, 235, 0.5)",
            borderColor: "rgba(54, 162, 235, 1)",
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          animation: { duration: 0 },
          scales: { y: { beginAtZero: true } }
        }
      });

    } catch (err) {
      console.error("❌ Failed to load sales data:", err);
      tableBody.innerHTML = `
        <tr>
          <td colspan="4" class="text-center text-danger">Error loading sales data</td>
        </tr>
      `;
    }
  }

  filterBtn.addEventListener("click", loadReports);

  // Initial load
  loadReports();
});
