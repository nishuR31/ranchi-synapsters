import axios from "axios";
import type {
  GraphSnapshot,
  GraphStats,
  FraudRing,
  Kingpin,
  EntityTimeline,
  RiskAssessment,
  AnomalyDetection,
} from "./types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || "http://localhost:8000",
});

export async function fetchGraphStats(): Promise<GraphStats> {
  const { data } = await api.get<GraphStats>("/api/v1/system/graph/stats");
  return data;
}

export async function fetchGraphSnapshot(limit = 400): Promise<GraphSnapshot> {
  const { data } = await api.get<GraphSnapshot>("/api/v1/intelligence/graph", {
    params: { limit },
  });
  return data;
}

export async function fetchFraudRings(): Promise<FraudRing[]> {
  const { data } = await api.get<FraudRing[]>("/api/v1/intelligence/clusters");
  return data;
}

export async function fetchKingpins(top = 10): Promise<Kingpin[]> {
  const { data } = await api.get<Kingpin[]>("/api/v1/intelligence/kingpins", {
    params: { top_k: top },
  });
  return data;
}

export async function fetchTimeline(entityId: string): Promise<EntityTimeline> {
  const { data } = await api.get<EntityTimeline>(
    `/api/v1/intelligence/timeline/${encodeURIComponent(entityId)}`
  );
  return data;
}

export async function fetchRisk(entityId: string): Promise<RiskAssessment> {
  const { data } = await api.get<RiskAssessment>(
    `/api/v1/intelligence/risk/${encodeURIComponent(entityId)}`
  );
  return data;
}

export async function fetchAnomalies(
  entityId: string
): Promise<AnomalyDetection[]> {
  const { data } = await api.get<AnomalyDetection[]>(
    `/api/v1/intelligence/anomalies/${encodeURIComponent(entityId)}`
  );
  return data;
}

export async function uploadDataset(fileType: string, file: File) {
  const form = new FormData();
  form.append("file_type", fileType);
  form.append("file", file);
  const { data } = await api.post("/api/v1/data/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export function formatNumber(num: number | undefined, decimals = 0): string {
  if (num === undefined || num === null) return "0";
  return Number(num).toLocaleString("en-IN", {
    maximumFractionDigits: decimals,
  });
}

export const API_BASE = api.defaults.baseURL;
