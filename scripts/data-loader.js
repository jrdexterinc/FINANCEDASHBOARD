// Data loader with SharePoint integration
class DashboardData {
  constructor() {
    this.dataPath = "./data/"; // Relative path to JSON files
    this.cache = {};
  }

  // Load JSON file from SharePoint library
  async loadJSON(filename) {
    if (this.cache[filename]) {
      return this.cache[filename];
    }

    try {
      const response = await fetch(`${this.dataPath}${filename}`);
      if (!response.ok) {
        throw new Error(`Failed to load ${filename}`);
      }
      const data = await response.json();
      this.cache[filename] = data;
      return data;
    } catch (error) {
      console.error("Error loading data:", error);
      return null;
    }
  }

  // Get current week's data
  async getCurrentWeekData() {
    const data = await this.loadJSON("contributions_2026.json");
    // Add filtering logic here
    return data.currentWeek;
  }

  // Get budget comparison data
  async getBudgetData() {
    return await this.loadJSON("budget_2026.json");
  }

  // Calculate metrics
  calculateVariance(actual, budget) {
    const variance = actual - budget;
    const percentage = (variance / budget) * 100;
    return {
      amount: variance,
      percentage: percentage,
      isPositive: variance >= 0,
    };
  }

  formatCurrency(amount) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  formatPercentage(value) {
    const sign = value >= 0 ? "+" : "";
    return `${sign}${value.toFixed(2)}%`;
  }
}
