import { formatNumber } from "../api/client";
import type { GraphStats } from "../api/types";
import { motion } from "framer-motion";

interface Props {
  stats?: GraphStats;
}

export default function StatsGrid({ stats }: Props) {
  const cards = [
    {
      label: "Nodes",
      value: formatNumber(stats?.total_nodes),
      accent: "from-sky-400/60 to-cyan-300/50",
    },
    {
      label: "Relationships",
      value: formatNumber(stats?.total_relationships),
      accent: "from-violet-400/60 to-fuchsia-300/50",
    },
    {
      label: "Density",
      value: stats ? `${(stats.density * 100).toFixed(2)}%` : "—",
      accent: "from-emerald-400/60 to-lime-300/50",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {cards.map((card) => (
        <motion.div
          key={card.label}
          className="glass rounded-xl p-4 border border-slate-700/40"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <p className="text-sm text-slate-400">{card.label}</p>
          <p className="text-2xl font-semibold text-sky-50 mt-1">
            {card.value}
          </p>
          <div
            className={`h-1 mt-3 rounded-full bg-gradient-to-r ${card.accent}`}
          ></div>
        </motion.div>
      ))}
    </div>
  );
}
