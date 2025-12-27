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
      setStatus("Select a CSV file first");
      return;
    }
    setLoading(true);
    setStatus("Uploading...");
    try {
      console.log("Uploading to API...");
      const res = await uploadDataset(fileType, file);
      console.log("Upload response:", res);
      if (res.status === "success") {
        const inserted = res.ingestion_result?.inserted || 0;
        const errors = res.ingestion_result?.errors || 0;
        setStatus(`✓ ${file.name} uploaded! Inserted: ${inserted} rows, Errors: ${errors}`);
        setFile(null);
        onUploaded?.();
      } else {
        setStatus(`Status: ${res.status}`);
      }
    } catch (err: any) {
      console.error("Upload error:", err);
      let errorMsg = "Upload failed";
      if (err?.response?.data?.detail) {
        errorMsg = typeof err.response.data.detail === 'string' 
          ? err.response.data.detail 
          : JSON.stringify(err.response.data.detail);
      } else if (err?.message) {
        errorMsg = err.message;
      }
      setStatus(`✗ Error: ${errorMsg}`);
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
          className="px-3 py-2 border border-slate-600 rounded-lg bg-slate-800 text-slate-200 text-sm cursor-pointer hover:bg-slate-700 transition"
        />
        {file && <span className="text-sm text-emerald-400">📄 {file.name}</span>}
        <button
          onClick={handleUpload}
          className="px-6 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white font-semibold text-sm transition disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={loading || !file}
        >
          {loading ? "Uploading…" : file ? " Upload" : " Select file first"}
        </button>
      </div>
      {status && <p className="text-sm text-slate-300 mt-2">{status}</p>}
    </Section>
  );
}
