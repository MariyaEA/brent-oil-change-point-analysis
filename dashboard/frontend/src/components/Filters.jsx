import { CalendarRange, Filter, RefreshCw } from "lucide-react";

export default function Filters({ filters, categories, loading, onChange, onApply }) {
  return (
    <section className="filters panel">
      <div className="panel-title-row">
        <div>
          <span className="section-kicker">Explore the market</span>
          <h2>Analysis controls</h2>
        </div>
        <CalendarRange size={22} />
      </div>
      <div className="filter-grid">
        <label>
          Start date
          <input
            type="date"
            value={filters.start_date}
            onChange={(event) => onChange("start_date", event.target.value)}
          />
        </label>
        <label>
          End date
          <input
            type="date"
            value={filters.end_date}
            onChange={(event) => onChange("end_date", event.target.value)}
          />
        </label>
        <label>
          Resolution
          <select
            value={filters.frequency}
            onChange={(event) => onChange("frequency", event.target.value)}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </label>
        <label>
          Event category
          <select
            value={filters.category}
            onChange={(event) => onChange("category", event.target.value)}
          >
            <option value="all">All categories</option>
            {categories.map((category) => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </label>
        <button type="button" className="primary-button" onClick={onApply} disabled={loading}>
          {loading ? <RefreshCw className="spin" size={18} /> : <Filter size={18} />}
          {loading ? "Updating" : "Apply filters"}
        </button>
      </div>
    </section>
  );
}
