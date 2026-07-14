import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { TrendingUp } from "lucide-react";

const formatDate = (timestamp) => new Date(timestamp).toLocaleDateString("en-GB", {
  month: "short",
  year: "2-digit",
});

function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <span>{new Date(point.ts).toLocaleDateString("en-GB", { dateStyle: "medium" })}</span>
      <strong>${point.price.toFixed(2)} / bbl</strong>
    </div>
  );
}

export default function PriceChart({ prices, events, changePoint, selectedEvent, loading }) {
  const chartData = prices.map((point) => ({
    ...point,
    ts: new Date(`${point.date}T00:00:00`).getTime(),
  }));
  const visibleEvents = events.slice(0, 14);

  return (
    <section className="panel chart-panel">
      <div className="panel-title-row">
        <div>
          <span className="section-kicker">Historical prices and event overlay</span>
          <h2>Brent price regimes</h2>
        </div>
        <TrendingUp size={23} />
      </div>

      <div className="chart-legend">
        <span><i className="legend-price" /> Brent price</span>
        <span><i className="legend-change" /> Bayesian change point</span>
        <span><i className="legend-event" /> Researched event</span>
      </div>

      <div className="chart-wrap" aria-busy={loading}>
        {chartData.length === 0 ? (
          <div className="empty-state">No prices match the selected dates.</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 18, right: 20, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis
                type="number"
                dataKey="ts"
                domain={["dataMin", "dataMax"]}
                scale="time"
                tickFormatter={formatDate}
                minTickGap={44}
              />
              <YAxis width={54} tickFormatter={(value) => `$${value}`} domain={["auto", "auto"]} />
              <Tooltip content={<ChartTooltip />} />
              {visibleEvents.map((event) => (
                <ReferenceLine
                  key={`${event.date}-${event.name}`}
                  x={new Date(`${event.date}T00:00:00`).getTime()}
                  stroke="#7b879b"
                  strokeOpacity={selectedEvent?.name === event.name ? 0.9 : 0.25}
                  strokeDasharray="2 5"
                />
              ))}
              {changePoint && (
                <ReferenceLine
                  x={new Date(`${changePoint.change_point_date}T00:00:00`).getTime()}
                  stroke="#f49b45"
                  strokeWidth={2.4}
                  strokeDasharray="7 5"
                  label={{ value: "Detected shift", position: "insideTopRight", fill: "#f49b45", fontSize: 12 }}
                />
              )}
              {selectedEvent && (
                <ReferenceLine
                  x={new Date(`${selectedEvent.date}T00:00:00`).getTime()}
                  stroke="#59d0b3"
                  strokeWidth={2}
                  label={{ value: "Selected event", position: "insideTopLeft", fill: "#59d0b3", fontSize: 12 }}
                />
              )}
              <Line
                type="monotone"
                dataKey="price"
                stroke="#8bbcff"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </section>
  );
}
