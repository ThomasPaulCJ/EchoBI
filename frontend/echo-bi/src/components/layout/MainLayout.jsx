// src/components/layout/MainLayout.jsx
import React, { useState } from "react";
import Header from "./Header";
import Sidebar from "./Sidebar";
import Footer from "./Footer";
import "./MainLayout.css";

export default function MainLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const closeSidebar = () => setSidebarOpen(false);

  return (
    <div className="app">
      <Header onMenuClick={toggleSidebar} />
      <div className="app-layout">
        <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
        <main className="app-main">
          <div className="page-content">
            {children}
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}
