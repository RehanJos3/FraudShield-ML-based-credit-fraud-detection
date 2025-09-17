import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navigation from "./components/Navigation";
import Dashboard from "./components/Dashboard";
import FraudPredictor from "./components/FraudPredictor";
import Analytics from "./components/Analytics";
import "./App.css";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <div className="flex min-h-screen bg-gray-50">
          <Navigation />
          <main className="flex-1 overflow-x-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/predict" element={<FraudPredictor />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;