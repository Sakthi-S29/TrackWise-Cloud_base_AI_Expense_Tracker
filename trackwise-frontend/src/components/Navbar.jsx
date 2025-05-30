import React from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="bg-blue-600 text-white px-6 py-4 flex justify-between items-center shadow-md">
      <h1 className="text-2xl font-bold tracking-wide flex items-center gap-2">
        <span role="img" aria-label="logo">💰</span> TrackWise
      </h1>
      <div className="space-x-6 text-lg">
        <Link to="/" className="hover:text-yellow-300">Dashboard</Link>
        <Link to="/add" className="hover:text-yellow-300">Add Entry</Link>
        <Link to="/chat" className="hover:text-yellow-300">Chatbot</Link>
      </div>
    </nav>
  );
}

export default Navbar;
