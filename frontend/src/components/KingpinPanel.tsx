import type { Kingpin } from "../api/types";
import { motion } from "framer-motion";
import { formatNumber } from "../api/client";
import clsx from "clsx";
import Section from "./Section";

interface Props {
  data?: Kingpin[];
}

const riskTone: Record<string, string> = {
  HIGH: "bg-red-500/10 text-red-200 border-red-500/30",
  MEDIUM: "bg-amber-500/10 text-amber-200 border-amber-500/30",
  LOW: "bg-sky-500/10 text-sky-200 border-sky-500/30",
};

export default function KingpinPanel({ data }: Props) {
  return (
    <Section
      title="Kingpin Panel"
      subtitle="Influence scored via PageRank + Betweenness + degree"
    >
      <div className="space-y-3">
        {data?.length ? (
          data.map((kp, idx) => (
            <motion.div
              key={kp.entity_id}
              className="glass p-4 rounded-xl border border-slate-700/40 flex items-center justify-between"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.03 }}
            >
              <div>
                <p className="text-sky-50 font-semibold">{kp.entity_id}</p>
                <p className="text-slate-400 text-sm">
                  {kp.entity_type.toUpperCase()} •{" "}
                  {formatNumber(kp.connections)} connections
                </p>
                <div className="flex gap-3 text-xs text-slate-300 mt-2">
                  <span>Influence: {kp.influence_score.toFixed(3)}</span>
                  <span>PR: {kp.pagerank_score.toFixed(4)}</span>
                  <span>Betw.: {kp.betweenness_centrality.toFixed(4)}</span>
                </div>
              </div>
              <span className={clsx("badge", riskTone[kp.risk_level])}>
                {kp.risk_level}
              </span>
            </motion.div>
          ))
        ) : (
          <p className="text-slate-500">
            No kingpins yet. Upload data to see influence leaders.
          </p>
        )}
      </div>
    </Section>
  );
}
