import { Activity, CircleDot } from "lucide-react";

export default function Header({ apiReady }) {
  return (
    <header className="topbar">
      <div className="brand-mark">BE</div>
      <div className="brand-copy">
        <span className="eyebrow">Birhan Energies</span>
        <h1>Brent Market Intelligence</h1>
      </div>
      <div className={`status-pill ${apiReady ? "online" : "offline"}`}>
        {apiReady ? <Activity size={16} /> : <CircleDot size={16} />}
        {apiReady ? "Live analysis" : "Connecting"}
      </div>
    </header>
  );
}
