// Main dashboard initialization
const dashboard = new DashboardData();

async function initializeDashboard() {
  try {
    // Load data
    const weekData = await dashboard.getCurrentWeekData();
    const budgetData = await dashboard.getBudgetData();

    // Update KPIs
    updateKPIs(weekData);

    // Initialize charts
    createWeeklyTrendChart(weekData.weeklyTrend);
    createGivingMethodChart(weekData.givingMethods);
    createDonationCategoryChart(weekData.donationCategories);
    createBudgetChart(weekData, budgetData);
    createYoYChart(weekData.yoyComparison);

    // Update large gifts table
    updateLargeGiftsTable(weekData.largeGifts);

    // Set report week/published date from JSON
    const rawData = await dashboard.loadJSON("contributions_2026.json");
    if (rawData && rawData.reportWeekEnding) {
      const reportDate = new Date(rawData.reportWeekEnding);
      document.getElementById("reportWeek").textContent =
        reportDate.toLocaleString("en-US", {
          month: "short",
          day: "numeric",
          year: "numeric",
        });
    }

    // Set last updated time
    document.getElementById("lastUpdate").textContent =
      new Date().toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });
  } catch (error) {
    console.error("Dashboard initialization failed:", error);
    showError("Unable to load dashboard data. Please contact Finance.");
  }
}

function updateKPIs(data) {
  // WTD
  document.getElementById("wtdContributions").textContent =
    dashboard.formatCurrency(data.wtd.actual);

  const wtdVariance = dashboard.calculateVariance(
    data.wtd.actual,
    data.wtd.budget,
  );
  const wtdVarianceEl = document.getElementById("wtdVariance");
  wtdVarianceEl.textContent = dashboard.formatPercentage(
    wtdVariance.percentage,
  );
  wtdVarianceEl.className = `kpi-variance ${wtdVariance.isPositive ? "positive" : "negative"}`;

  // MTD
  document.getElementById("mtdContributions").textContent =
    dashboard.formatCurrency(data.mtd.actual);

  const mtdVariance = dashboard.calculateVariance(
    data.mtd.actual,
    data.mtd.budget,
  );
  const mtdVarianceEl = document.getElementById("mtdVariance");
  mtdVarianceEl.textContent = dashboard.formatPercentage(
    mtdVariance.percentage,
  );
  mtdVarianceEl.className = `kpi-variance ${mtdVariance.isPositive ? "positive" : "negative"}`;

  // YTD
  document.getElementById("ytdContributions").textContent =
    dashboard.formatCurrency(data.ytd.actual);

  const ytdVariance = dashboard.calculateVariance(
    data.ytd.actual,
    data.ytd.budget,
  );
  const ytdVarianceEl = document.getElementById("ytdVariance");
  ytdVarianceEl.textContent = dashboard.formatPercentage(
    ytdVariance.percentage,
  );
  ytdVarianceEl.className = `kpi-variance ${ytdVariance.isPositive ? "positive" : "negative"}`;

  // Givers
  document.getElementById("distinctGivers").textContent =
    data.distinctGivers.current.toLocaleString();

  const giversChange =
    data.distinctGivers.current - data.distinctGivers.previous;
  const giversChangeEl = document.getElementById("giversChange");
  giversChangeEl.textContent =
    (giversChange > 0 ? "+" : "") + giversChange + " givers";
  giversChangeEl.className = `kpi-change ${giversChange >= 0 ? "positive" : "negative"}`;
}

function updateLargeGiftsTable(gifts) {
  const tbody = document.getElementById("largeGiftsBody");
  tbody.innerHTML = "";

  if (!gifts || gifts.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="4" style="text-align: center;">No large gifts this period</td></tr>';
    return;
  }

  gifts.forEach((gift) => {
    const row = tbody.insertRow();
    row.innerHTML = `
            <td>${new Date(gift.date).toLocaleDateString()}</td>
            <td>${dashboard.formatCurrency(gift.amount)}</td>
            <td>${gift.method}</td>
            <td>${gift.category}</td>
        `;
  });
}

function showError(message) {
  const container = document.querySelector(".dashboard-container");
  container.innerHTML = `
        <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; margin: 20px;">
            <h3>Error Loading Dashboard</h3>
            <p>${message}</p>
        </div>
    `;
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", initializeDashboard);

// Auto-refresh every 5 minutes
setInterval(initializeDashboard, 5 * 60 * 1000);
