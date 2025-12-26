import { useState } from "react";
import { uploadDataset } from "../api/client";
import Section from "./Section";

const fileTypes = [
  { value: "calls", label: "Call Detail Records (calls)" },
  { value: "transactions", label: "Bank transactions" },
  { value: "devices", label: "Device/IP logs" },
  { value: "sims", label: "SIM metadata" },
  { value: "complaints", label: "Complaints" },
];

interface Props {
  onUploaded?: () => void;
}

export default function UploadPanel({ onUploaded }: Props) {
  const [fileType, setFileType] = useState("calls");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      setStatus("Select a CSV to upload");
      return;
    }
    setLoading(true);
    setStatus(null);
    try {
      const res = await uploadDataset(fileType, file);
      setStatus(`Uploaded ${file.name}: ${res.status}`);
      onUploaded?.();
    } catch (err: any) {
      setStatus(err?.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Section
      title="Data Ingestion"
      subtitle="Upload CSVs; pipeline normalizes + writes to Neo4j"
    >
      <div className="flex flex-col md:flex-row md:items-center gap-3">
        <select
          value={fileType}
          onChange={(e) => setFileType(e.target.value)}
          className="bg-slate-900/60 border border-slate-700/60 text-slate-100 rounded-lg px-3 py-2 text-sm"
        >
          {fileTypes.map((f) => (
            <option key={f.value} value={f.value}>
              {f.label}
            </option>
          ))}
        </select>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="text-slate-200 text-sm"
        />
        <button
          onClick={handleUpload}
          className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm"
          disabled={loading}
        >
          {loading ? "Uploading…" : "Upload"}
        </button>
      </div>
      {status && <p className="text-sm text-slate-300 mt-2">{status}</p>}
    </Section>
  );
}
