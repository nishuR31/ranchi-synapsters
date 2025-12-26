import CytoscapeComponent from "react-cytoscapejs";
import type { GraphSnapshot, GraphNode } from "../api/types";
import { useMemo, useState } from "react";
import Section from "./Section";

interface Props {
  snapshot?: GraphSnapshot;
}

const riskColor = (node: GraphNode) => {
  if (node.risk_level === "HIGH") return "#ef4444";
  if (node.risk_level === "MEDIUM") return "#f59e0b";
  return "#38bdf8";
};

export default function GraphView({ snapshot }: Props) {
  const [layoutKey, setLayoutKey] = useState(0);

  const elements = useMemo(() => {
    if (!snapshot) return [];
    const nodes = snapshot.nodes.map((n) => ({
      data: {
        id: n.id,
        label: `${n.label}: ${n.entity_id}`,
        risk: n.risk_level,
        weight: Math.max(1, n.degree),
      },
      classes: n.risk_level?.toLowerCase(),
    }));
    const edges = snapshot.edges.map((e, idx) => ({
      data: {
        id: `e-${idx}`,
        source: e.source,
        target: e.target,
        label: e.relation,
        weight: e.weight,
      },
    }));
    return [...nodes, ...edges];
  }, [snapshot]);

  return (
    <Section
      title="Live Network Graph"
      subtitle="Nodes sized by degree, colored by risk; hover to inspect relationships"
      right={
        <button
          className="badge bg-white/5 text-sky-100 hover:bg-white/10"
          onClick={() => setLayoutKey((k) => k + 1)}
        >
          Re-run layout
        </button>
      }
      className="col-span-2"
    >
      <div className="h-[460px] rounded-xl overflow-hidden border border-slate-700/40">
        {snapshot ? (
          <CytoscapeComponent
            key={layoutKey}
            elements={elements as any}
            style={{ width: "100%", height: "100%" }}
            layout={{ name: "cose", animate: true, fit: true }}
            stylesheet={[
              {
                selector: "node",
                style: {
                  "background-color": (ele: any) =>
                    riskColor({ risk_level: ele.data("risk") } as GraphNode),
                  label: "data(label)",
                  color: "#e2e8f0",
                  "font-size": 10,
                  width: "mapData(weight, 1, 50000, 16, 42)",
                  height: "mapData(weight, 1, 50000, 16, 42)",
                  "text-wrap": "wrap",
                  "text-max-width": 120,
                  "text-valign": "center",
                  "text-halign": "center",
                },
              },
              {
                selector: "edge",
                style: {
                  width: 1.4,
                  "line-color": "#334155",
                  "curve-style": "bezier",
                  "target-arrow-shape": "triangle",
                  "target-arrow-color": "#334155",
                  label: "data(label)",
                  "font-size": 9,
                  "text-rotation": "autorotate",
                  "text-background-color": "rgba(15,23,42,0.7)",
                  "text-background-opacity": 1,
                  "text-background-padding": 2,
                },
              },
              {
                selector: ".high",
                style: { "border-color": "#ef4444", "border-width": 2 },
              },
              {
                selector: ".medium",
                style: { "border-color": "#f59e0b", "border-width": 2 },
              },
              {
                selector: ".low",
                style: { "border-color": "#38bdf8", "border-width": 2 },
              },
            ]}
          />
        ) : (
          <div className="h-full flex items-center justify-center text-slate-400">
            Graph loading…
          </div>
        )}
      </div>
    </Section>
  );
}
