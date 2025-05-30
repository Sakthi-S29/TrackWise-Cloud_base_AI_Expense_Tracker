import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import AddEntry from './pages/AddEntry';
import Chatbot from './pages/Chatbot';

function App() {
  return (
    <Router>
      <Navbar />
      <main className="max-w-6xl mx-auto py-10 px-6 sm:px-10">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/add" element={<AddEntry />} />
          <Route path="/chat" element={<Chatbot />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;