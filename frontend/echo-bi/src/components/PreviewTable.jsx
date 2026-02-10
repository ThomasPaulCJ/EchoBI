// src/components/PreviewTable.jsx
import React from "react";

export default function PreviewTable({ preview }) {
  if (!preview || preview.length === 0) return null;
  
  const cols = Object.keys(preview[0]);
  
  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            {cols.map((c) => <th key={c}>{c}</th>)}
          </tr>
        </thead>
        <tbody>
          {preview.map((row, idx) => (
            <tr key={idx}>
              {cols.map((c) => (
                <td key={c + idx}>{String(row[c] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
