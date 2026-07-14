import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, BarChart3, Database, Gauge, TrendingDown } from "lucide-react";
import { api } from "./services/api";
import Header from "./components/Header";
import StatCard from "./components/StatCard";
import Filters from "./components/Filters";
import PriceChart from "./components/PriceChart";
import ChangePointCard from "./components/ChangePointCard";
import EventExplorer from "./components/EventExplorer";
import CorrelationTable from "./components/CorrelationTable";

const initialFilters = {
  start_date: "2013-01-01",
  end_date: "2016-12-31",
  frequency: "daily",
  category: "all",
};

export default function App() {
  const [filters, setFilters] = useState(initialFilters);
  const [summary, setSummary] = useState(null);
  const [changePoint, setChangePoint] = useState(null);
  const [prices, setPrices] = useState([]);
  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [correlations, setCorrelations] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadStaticResults = useCallback(async () => {
    const [summaryPayload, changePayload] = await Promise.all([
      api.summary(),
      api.changePoints(),
    ]);
    setSummary(summaryPayload);
    setChangePoint(changePayload.data[0]);
  }, []);

  const loadFilteredResults = useCallback(async (activeFilters) => {
    setLoading(true);
    setError("");
    try {
      const query = {
        start_date: activeFilters.start_date,
        end_date: activeFilters.end_date,
        frequency: activeFilters.frequency,
      };
      const eventQuery = {
        start_date: activeFilters.start_date,
        end_date: activeFilters.end_date,
        category: activeFilters.category,
      };
      const [pricePayload, eventPayload, correlationPayload] = await Promise.all([
        api.prices(query),
        api.events(eventQuery),
        api.correlations(query),
      ]);
      setPrices(pricePayload.data);
      setEvents(eventPayload.data);
      setCategories(eventPayload.categories);
      setCorrelations(correlationPayload.data);
      setSelectedEvent((current) => {
        if (current && eventPayload.data.some((item) => item.name === current.name)) return current;
        return eventPayload.data.find((item) => item.name.includes("30 million")) || eventPayload.data[0] || null;
      });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    (async () => {
      try {
        await loadStaticResults();
        await loadFilteredResults(initialFilters);
      } catch (requestError) {
        setError(requestError.message);
        setLoading(false);
      }
    })();
  }, [loadFilteredResults, loadStaticResults]);

  const updateFilter = (name, value) => setFilters((current) => ({ ...current, [name]: value }));

  return (
    <div className="app-shell">
      <Header apiReady={Boolean(summary) && !error} />
      <main>
        <section className="hero">
          <div>
            <span className="hero-tag">Change point analysis · 1987–2022</span>
            <h2>See when the oil market changed—and what happened nearby.</h2>
            <p>
              Explore Brent price regimes, Bayesian model output, and researched geopolitical,
              OPEC, sanctions, and economic events. Date alignment is presented as evidence for
              investigation, not proof of causality.
            </p>
          </div>
          <div className="hero-orbit" aria-hidden="true"><span /><span /><span /></div>
        </section>

        {error && (
          <div className="error-banner">
            <AlertTriangle size={20} />
            <div><strong>Dashboard data could not be loaded.</strong><span>{error}</span></div>
          </div>
        )}

        <section className="stats-grid">
          <StatCard icon={Database} label="Daily observations" value={summary ? summary.observations.toLocaleString() : "—"} note={summary ? `${summary.coverage_start} to ${summary.coverage_end}` : "Loading data"} />
          <StatCard icon={TrendingDown} label="Modeled level shift" value={summary ? `${summary.percent_change.toFixed(1)}%` : "—"} note="2014 event-centered window" />
          <StatCard icon={Gauge} label="Maximum R-hat" value={summary ? summary.maximum_r_hat.toFixed(4) : "—"} note="Convergence close to 1.00" />
          <StatCard icon={BarChart3} label="Average historical price" value={summary ? `$${summary.average_price}` : "—"} note="Nominal USD per barrel" />
        </section>

        <Filters
          filters={filters}
          categories={categories}
          loading={loading}
          onChange={updateFilter}
          onApply={() => loadFilteredResults(filters)}
        />

        <section className="analysis-grid">
          <PriceChart prices={prices} events={events} changePoint={changePoint} selectedEvent={selectedEvent} loading={loading} />
          <ChangePointCard result={changePoint} />
        </section>

        <section className="lower-grid">
          <EventExplorer events={events} selectedEvent={selectedEvent} onSelect={setSelectedEvent} />
          <CorrelationTable rows={correlations} />
        </section>
      </main>
      <footer>
        <span>Birhan Energies · Decision intelligence prototype</span>
        <span>Analysis by Mariamawit Ewnetu Alemu</span>
      </footer>
    </div>
  );
}
