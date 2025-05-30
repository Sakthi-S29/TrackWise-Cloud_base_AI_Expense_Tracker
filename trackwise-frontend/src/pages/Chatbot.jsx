import React, { useState } from 'react';

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    const userMessage = { sender: 'user', text: input };
    const botMessage = { sender: 'bot', text: `You asked: "${input}" (response goes here...)` };
    setMessages([...messages, userMessage, botMessage]);
    setInput('');
  };

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6 text-gray-900">Ask TrackWise</h2>
      <div className="h-80 overflow-y-auto border border-gray-300 p-4 mb-6 bg-white rounded-lg shadow-sm">
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-2 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
            <span className={`inline-block px-4 py-2 rounded-xl ${msg.sender === 'user' ? 'bg-blue-100' : 'bg-gray-200'}`}>{msg.text}</span>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          className="flex-grow border p-3 rounded-lg"
        />
        <button onClick={handleSend} className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">Send</button>
      </div>
    </div>
  );
}

export default Chatbot;