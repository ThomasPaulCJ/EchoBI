import React, { useState, useRef } from "react";
import { api } from "./api";
import { ChartBar, CloudUpload } from "lucide-react";

type PreviewRow = Record<string, any>;

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [previewRows, setPreviewRows] = useState<PreviewRow[]>([]);
  const [chartType, setChartType] = useState<string | null>(null);
  const [chartData, setChartData] = useState<any[] | null>(null);
  const fileRef = useRef<HTMLInputElement | null>(null);

  async function handleUpload(e?: React.ChangeEvent<HTMLInputElement>) {
    const f = e?.target.files?.[0];
    if (!f) return;
    setFile(f);
    setUploading(true);
    const fd = new FormData();
    fd.append("file", f);
    try {
      const res = await api.post("/upload", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setDatasetId(res.data.id);
      setColumns(res.data.columns || []);
      setPreviewRows(res.data.previewRows || []);
    } catch (err) {
      console.error(err);
      alert("Upload failed — check backend");
    } finally {
      setUploading(false);
    }
  }

  async function requestRecommend() {
    if (!datasetId) return alert("Upload dataset first");
    try {
      const r = await api.post("/recommend", { dataset_id: datasetId });
      setChartType(r.data.chart_type);
      // fetch chart data right away
      const cd = await api.post("/chartdata", {
        dataset_id: datasetId,
        chart_type: r.data.chart_type,
      });
      setChartData(cd.data.chartData);
    } catch (err) {
      console.error(err);
      alert("Recommendation failed");
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <div className="max-w-6xl mx-auto p-6">
        <header className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold">ECHO-BI — Frontend (Phase 2)</h1>
            <p className="text-sm text-slate-500">React + Vite + Tailwind • connected to FastAPI</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-2 px-3 py-1 bg-white border rounded">
              <ChartBar size={16} /> React
            </span>
          </div>
        </header>

        <main className="grid grid-cols-12 gap-6">
          <aside className="col-span-4 bg-white rounded-lg p-4 shadow">
            <label className="block mb-2 text-sm font-medium">Upload dataset (CSV / XLSX)</label>
            <div className="flex gap-2">
              <input
                ref={fileRef}
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleUpload}
                className="hidden"
              />
              <button
                onClick={() => fileRef.current?.click()}
                className="inline-flex items-center gap-2 px-3 py-2 rounded border bg-white"
              >
                <CloudUpload size={16} /> Choose file
              </button>
              <button
                onClick={requestRecommend}
                className="ml-auto px-3 py-2 rounded bg-sky-600 text-white"
              >
                Recommend Chart
              </button>
            </div>

            <div className="mt-4 text-xs text-slate-500">
              Dataset ID: <strong>{datasetId ?? "—"}</strong>
            </div>
            {uploading && <div className="mt-3 text-sm text-slate-500">Uploading…</div>}
          </aside>

          <section className="col-span-8">
            <div className="bg-white rounded-lg p-4 shadow mb-6">
              <h2 className="font-medium mb-3">Data preview</h2>
              <div className="overflow-x-auto">
                {previewRows.length > 0 ? (
                  <table className="min-w-full text-sm">
                    <thead className="text-left text-slate-600">
                      <tr>
                        {columns.map((c) => (
                          <th key={c} className="px-2 py-1">{c}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {previewRows.map((r, i) => (
                        <tr key={i} className="border-t">
                          {columns.map((c) => (
                            <td key={c} className="px-2 py-1">{String(r[c])}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="p-6 text-slate-400">No preview yet — upload a dataset.</div>
                )}
              </div>
            </div>

            <div className="bg-white rounded-lg p-4 shadow">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium">Chart</h3>
                <div className="text-sm text-slate-500">Predicted: <strong>{chartType ?? "—"}</strong></div>
              </div>

              <div className="min-h-[240px] border rounded flex items-center justify-center">
                {chartData ? (
                  <div className="text-sm text-slate-600 px-4">
                    <pre className="text-xs max-h-64 overflow-auto">{JSON.stringify(chartData, null, 2)}</pre>
                  </div>
                ) : (
                  <div className="text-slate-400">No chart data yet — click “Recommend Chart”.</div>
                )}
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
