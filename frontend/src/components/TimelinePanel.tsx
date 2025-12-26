import { useState } from "react";
import type {
  EntityTimeline,
  RiskAssessment,
  AnomalyDetection,
} from "../api/types";
import {
  fetchTimeline,
  fetchRisk,
  fetchAnomalies,
  formatNumber,
} from "../api/client";
import Section from "./Section";

export default function TimelinePanel() {
  const [entityId, setEntityId] = useState("");
  const [timeline, setTimeline] = useState<EntityTimeline | null>(null);
  const [risk, setRisk] = useState<RiskAssessment | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyDetection[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const lookup = async () => {
    if (!entityId.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const [t, r, a] = await Promise.all([
        fetchTimeline(entityId.trim()),
        fetchRisk(entityId.trim()),
        fetchAnomalies(entityId.trim()),
      ]);
      setTimeline(t);
      setRisk(r);
      setAnomalies(a);
    } catch (err: any) {
      setError(err?.message || "Lookup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Section
      title="Timeline & Risk"
      subtitle="Forensic sequence for any phone/account; includes risk + anomalies"
      right={
        <div className="flex gap-2">
          <input
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            placeholder="Enter phone (+91...) or account"
            className="bg-slate-900/60 border border-slate-700/60 text-slate-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
          <button
            onClick={lookup}
            className="px-3 py-2 text-sm rounded-lg bg-sky-600 hover:bg-sky-500 text-white"
            disabled={loading}
          >
            {loading ? "Loading…" : "Lookup"}
          </button>
        </div>
      }
    >
      {error && <p className="text-red-400 text-sm mb-3">{error}</p>}
      {risk && (
        <div className="glass rounded-xl p-4 border border-slate-700/40 mb-4 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Risk score</p>
            <p className="text-2xl font-semibold text-sky-50">
              {risk.risk_score.toFixed(1)} / 100
            </p>
            <p className="text-xs text-slate-400 mt-1">
              {risk.recommendations.join(" • ")}
            </p>
          </div>
          <span className="badge bg-white/5 text-sky-100 border border-slate-600">
            {risk.risk_level}
          </span>
        </div>
      )}

      {timeline ? (
        <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
          {timeline.events.map((ev, idx) => (
            <div
              key={`${ev.timestamp}-${idx}`}
              className="glass rounded-lg p-3 border border-slate-700/40"
            >
              <div className="flex items-center justify-between text-sm">
                <p className="text-sky-100 font-semibold">
                  {ev.event_type.toUpperCase()}
                </p>
                <p className="text-slate-400">
                  {new Date(ev.timestamp).toLocaleString()}
                </p>
              </div>
              <p className="text-slate-300 text-sm mt-1">
                {ev.from_entity} → {ev.to_entity}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                {JSON.stringify(ev.details)}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-slate-500 text-sm">
          Enter an entity and run lookup to view the forensic timeline.
        </p>
      )}

      {anomalies.length > 0 && (
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
          {anomalies.map((a, idx) => (
            <div
              key={`${a.anomaly_type}-${idx}`}
              className="glass rounded-lg p-3 border border-slate-700/40"
            >
              <p className="text-slate-300 text-sm">
                {a.anomaly_type.toUpperCase()}
              </p>
              <p className="text-slate-400 text-xs">
                Confidence: {(a.confidence * 100).toFixed(1)}%
              </p>
              <p className="text-slate-400 text-xs">Risk: {a.risk_level}</p>
              <p className="text-xs text-slate-500 mt-1">
                {JSON.stringify(a.details)}
              </p>
            </div>
          ))}
        </div>
      )}
    </Section>
  );
}
