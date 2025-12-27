import { useEffect, useState } from "react";
import {
  fetchGraphSnapshot,
  fetchGraphStats,
  fetchFraudRings,
  fetchKingpins,
} from "./api/client";
import type {
  GraphSnapshot,
  GraphStats,
  FraudRing,
  Kingpin,
} from "./api/types";
import StatsGrid from "./components/StatsGrid";
import GraphView from "./components/GraphView";
import KingpinPanel from "./components/KingpinPanel";
import FraudRingPanel from "./components/FraudRingPanel";
import TimelinePanel from "./components/TimelinePanel";
import UploadPanel from "./components/UploadPanel";

function App() {
  const [stats, setStats] = useState<GraphStats | undefined>();
  const [snapshot, setSnapshot] = useState<GraphSnapshot | undefined>();
  const [rings, setRings] = useState<FraudRing[] | undefined>();
  const [kingpins, setKingpins] = useState<Kingpin[] | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hydrate = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, g, r, k] = await Promise.all([
        fetchGraphStats(),
        fetchGraphSnapshot(),
        fetchFraudRings(),
        fetchKingpins(),
      ]);
      setStats(s);
      setSnapshot(g);
      setRings(r);
      setKingpins(k);
    } catch (err: any) {
      setError(err?.message || "Dashboard load failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    hydrate();
  }, []);

  return (
    <div className="min-h-screen pb-12">
      <header className="px-4 md:px-8 pt-6 pb-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400">CYBERCRIME COMMAND CENTER</p>
            <h1 className="text-3xl md:text-4xl font-bold text-sky-50 mt-1">
              Ranchi Synapsters
            </h1>
            <p className="text-slate-400 mt-2">
              Graph driven intel for fraud rings, kingpins, and money trails
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={hydrate}
              className="badge bg-white/10 text-slate-100 hover:bg-white/20"
              disabled={loading}
            >
              {loading ? "Refreshing…" : "Refresh"}
            </button>
          </div>
        </div>
        {error && <p className="text-red-400 text-sm mt-3">{error}</p>}
      </header>

      <main className="px-4 md:px-8 space-y-6">
        <StatsGrid stats={stats} />
        <UploadPanel onUploaded={hydrate} />

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <GraphView snapshot={snapshot} />
          <div className="space-y-6">
            <KingpinPanel data={kingpins} />
            <FraudRingPanel data={rings} />
          </div>
        </div>

        <TimelinePanel />
      </main>
    </div>
  );
}

export default App;
