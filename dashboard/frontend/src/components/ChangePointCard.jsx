import { BadgeCheck, CalendarClock, MoveDownRight, ShieldCheck } from "lucide-react";

export default function ChangePointCard({ result }) {
  if (!result) return null;
  const event = result.nearest_event;

  return (
    <section className="panel insight-panel">
      <div className="panel-title-row">
        <div>
          <span className="section-kicker">Bayesian model output</span>
          <h2>Detected structural break</h2>
        </div>
        <BadgeCheck size={24} />
      </div>

      <div className="change-date">
        <CalendarClock size={20} />
        <div>
          <span>Posterior median</span>
          <strong>{new Date(`${result.change_point_date}T00:00:00`).toLocaleDateString("en-GB", { dateStyle: "long" })}</strong>
        </div>
      </div>

      <div className="impact-box">
        <MoveDownRight size={24} />
        <div>
          <span>Estimated mean-price shift</span>
          <strong>{result.percent_change.toFixed(1)}%</strong>
          <p>${result.mu_before_mean.toFixed(2)} → ${result.mu_after_mean.toFixed(2)} per barrel</p>
        </div>
      </div>

      <dl className="model-details">
        <div><dt>94% date interval</dt><dd>{result.change_point_date_hdi_low} – {result.change_point_date_hdi_high}</dd></div>
        <div><dt>Maximum R-hat</dt><dd>{result.maximum_r_hat.toFixed(4)}</dd></div>
        <div><dt>Nearest event</dt><dd>{event.event_name}</dd></div>
        <div><dt>Calendar distance</dt><dd>{Math.abs(event.distance_days)} days</dd></div>
      </dl>

      <div className="guardrail">
        <ShieldCheck size={18} />
        <p>{event.interpretation_guardrail}</p>
      </div>
    </section>
  );
}
