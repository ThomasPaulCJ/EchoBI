import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { MainLayout } from "./components/layout";
import { HomePage, UploadPage, AnalysisPage, PreprocessingPage, InsightsPage, DashboardPage } from "./pages";
import "./App.css";

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/preprocessing" element={<PreprocessingPage />} />
          <Route path="/insights" element={<InsightsPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
