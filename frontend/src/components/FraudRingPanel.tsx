import type { FraudRing } from "../api/types";
import { motion } from "framer-motion";
import { formatNumber } from "../api/client";
import Section from "./Section";

interface Props {
  data?: FraudRing[];
}

const ringPalette = [
  "from-sky-500/30 to-cyan-400/20",
  "from-fuchsia-500/30 to-purple-400/20",
  "from-emerald-500/30 to-lime-400/20",
];

export default function FraudRingPanel({ data }: Props) {
  return (
    <Section
      title="Fraud Rings"
      subtitle="Louvain communities across calls + transactions"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data?.length ? (
          data.map((ring, idx) => (
            <motion.div
              key={ring.ring_id}
              className={`glass rounded-xl p-4 border border-slate-700/40 bg-gradient-to-br ${
                ringPalette[idx % ringPalette.length]
              }`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.02 }}
            >
              <div className="bg-white/5 rounded-lg p-3 mb-3" />
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-300 text-sm">
                    {ring.ring_type.toUpperCase()}
                  </p>
                  <h3 className="text-xl font-semibold text-sky-50">
                    {ring.ring_id}
                  </h3>
                </div>
                <div className="text-right text-sm text-slate-300">
                  <p>
                    Members:{" "}
                    <span className="text-sky-100 font-semibold">
                      {ring.member_count}
                    </span>
                  </p>
                  <p>
                    Risk:{" "}
                    <span className="text-red-300 font-semibold">
                      {ring.risk_score.toFixed(1)}
                    </span>
                  </p>
                </div>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-3 text-sm text-slate-300">
                <div>
                  <p className="text-slate-400 text-xs">Calls</p>
                  <p className="text-sky-100 font-semibold">
                    {formatNumber(ring.total_calls)}
                  </p>
                </div>
                <div>
                  <p className="text-slate-400 text-xs">Money moved</p>
                  <p className="text-emerald-200 font-semibold">
                    ₹{formatNumber(ring.total_money_moved, 2)}
                  </p>
                </div>
              </div>
              <p className="text-xs text-slate-400 mt-3">
                Confidence: {(ring.confidence * 100).toFixed(1)}%
              </p>
            </motion.div>
          ))
        ) : (
          <p className="text-slate-500">
            No rings yet. Upload CDRs and transactions.
          </p>
        )}
      </div>
    </Section>
  );
}
