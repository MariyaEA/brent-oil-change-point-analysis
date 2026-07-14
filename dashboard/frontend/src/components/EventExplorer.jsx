import { ArrowUpRight, Landmark, Radio } from "lucide-react";

export default function EventExplorer({ events, selectedEvent, onSelect }) {
  return (
    <section className="panel events-panel">
      <div className="panel-title-row">
        <div>
          <span className="section-kicker">Research catalogue</span>
          <h2>Events in the selected period</h2>
        </div>
        <Landmark size={23} />
      </div>

      <div className="event-list">
        {events.length === 0 ? (
          <div className="empty-state">No researched events match these filters.</div>
        ) : events.map((event) => (
          <button
            type="button"
            className={`event-row ${selectedEvent?.name === event.name ? "selected" : ""}`}
            key={`${event.date}-${event.name}`}
            onClick={() => onSelect(event)}
          >
            <span className="event-radio"><Radio size={15} /></span>
            <span className="event-date">{new Date(`${event.date}T00:00:00`).toLocaleDateString("en-GB", { month: "short", year: "numeric" })}</span>
            <span className="event-copy">
              <strong>{event.name}</strong>
              <small>{event.category} · Expected pressure: {event.pressure}</small>
            </span>
            <ArrowUpRight size={17} />
          </button>
        ))}
      </div>
    </section>
  );
}
