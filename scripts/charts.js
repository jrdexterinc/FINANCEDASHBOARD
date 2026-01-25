// Chart instances for cleanup
let chartInstances = {};

// Create Weekly Contributions Trend Chart
function createWeeklyTrendChart(data) {
  if (chartInstances.weeklyTrend) {
    chartInstances.weeklyTrend.destroy();
  }

  const ctx = document.getElementById("weeklyTrendChart").getContext("2d");
  chartInstances.weeklyTrend = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.map((item) => item.week),
      datasets: [
        {
          label: "Weekly Contributions",
          data: data.map((item) => item.amount),
          borderColor: "#2563eb",
          backgroundColor: "rgba(37, 99, 235, 0.1)",
          tension: 0.4,
          fill: true,
          pointRadius: 5,
          pointBackgroundColor: "#2563eb",
          pointBorderColor: "#fff",
          pointBorderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: true,
          position: "top",
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return "$" + value.toLocaleString();
            },
          },
        },
      },
    },
  });
}

// Create Giving Method Distribution Chart
function createGivingMethodChart(data) {
  if (chartInstances.givingMethod) {
    chartInstances.givingMethod.destroy();
  }

  const ctx = document.getElementById("givingMethodChart").getContext("2d");
  const colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];

  chartInstances.givingMethod = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: Object.keys(data),
      datasets: [
        {
          data: Object.values(data),
          backgroundColor: colors,
          borderColor: "#fff",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: "bottom",
        },
      },
    },
  });
}

// Create Budget vs Actual Chart
function createBudgetChart(weekData, budgetData) {
  if (chartInstances.budget) {
    chartInstances.budget.destroy();
  }

  const ctx = document.getElementById("budgetChart").getContext("2d");
  const categories = budgetData.categories;

  chartInstances.budget = new Chart(ctx, {
    type: "bar",
    data: {
      labels: categories.map((cat) => cat.name),
      datasets: [
        {
          label: "Budgeted",
          data: categories.map((cat) => cat.budgeted),
          backgroundColor: "#e5e7eb",
          borderRadius: 4,
        },
        {
          label: "Spent",
          data: categories.map((cat) => cat.spent),
          backgroundColor: "#2563eb",
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      indexAxis: "y",
      plugins: {
        legend: {
          position: "top",
        },
      },
      scales: {
        x: {
          ticks: {
            callback: function (value) {
              return "$" + value.toLocaleString();
            },
          },
        },
      },
    },
  });
}

// Create Year-over-Year Comparison Chart
function createYoYChart(data) {
  if (chartInstances.yoy) {
    chartInstances.yoy.destroy();
  }

  const ctx = document.getElementById("yoyChart").getContext("2d");

  chartInstances.yoy = new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.map((item) => item.month),
      datasets: [
        {
          label: "2025",
          data: data.map((item) => item.previous),
          backgroundColor: "#d1d5db",
          borderRadius: 4,
        },
        {
          label: "2026",
          data: data.map((item) => item.current),
          backgroundColor: "#10b981",
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: "top",
        },
      },
      scales: {
        y: {
          ticks: {
            callback: function (value) {
              return "$" + value.toLocaleString();
            },
          },
        },
      },
    },
  });
}
