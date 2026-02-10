// src/pages/AboutPage.jsx
import React from "react";
import { Card } from "../components/common";
import "./AboutPage.css";

export default function AboutPage() {
  const teamMembers = [
    { name: "Manu Mathew", initial: "MM" },
    { name: "Thomas Paul CJ", initial: "TP" },
    { name: "Vidhusankar CH", initial: "VC" },
    { name: "Nayif Nazar", initial: "NN" },
  ];

  return (
    <div className="about-page">
      <div className="about-content">
        <div className="about-header">
          <div className="about-logo">E</div>
          <h1>EchoBI</h1>
          <p className="about-tagline">Self-Service Analytics Platform</p>
          <span className="about-version">v2.0</span>
        </div>

        <Card className="about-card">
          <p className="about-description">
            A no-code analytics platform that transforms raw data into actionable 
            insights with intelligent classification, preprocessing, and visualization.
          </p>
        </Card>

        <div className="team-section">
          <h2>Team</h2>
          <div className="team-grid">
            {teamMembers.map((member, idx) => (
              <div key={idx} className="team-member">
                <div className="member-avatar">{member.initial}</div>
                <span className="member-name">{member.name}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="about-footer">
          <p>© 2026 EchoBI Project</p>
        </div>
      </div>
    </div>
  );
}
