import { BarChart3 } from "lucide-react";

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  const number = Number(value);
  return `${number > 0 ? "+" : ""}${number.toFixed(1)}%`;
}

export default function CorrelationTable({ rows }) {
  return (
    <section className="panel table-panel">
      <div className="panel-title-row">
        <div>
          <span className="section-kicker">Descriptive association only</span>
          <h2>Largest event-window movements</h2>
        </div>
        <BarChart3 size={23} />
      </div>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Event</th><th>Category</th><th>5-day to 5-day move</th></tr></thead>
          <tbody>
            {rows.slice(0, 7).map((row) => (
              <tr key={`${row.event_date}-${row.event_name}`}>
                <td><strong>{row.event_name}</strong><span>{row.event_date}</span></td>
                <td>{row.category}</td>
                <td className={Number(row.pre_to_post_change_pct) < 0 ? "negative" : "positive"}>
                  {formatPercent(row.pre_to_post_change_pct)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
