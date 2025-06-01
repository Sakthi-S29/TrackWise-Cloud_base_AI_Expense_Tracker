import React, { useEffect, useState } from 'react';

function Dashboard() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const res = await fetch('https://zkcuaxz8b9.execute-api.us-east-1.amazonaws.com/get-transactions'); // Replace if needed
        const data = await res.json();
        setRecords(data);
      } catch (err) {
        console.error('Error fetching records:', err);
        setError('Failed to fetch data.');
      } finally {
        setLoading(false);
      }
    };
    fetchRecords();
  }, []);

  const income = records
    .filter((r) => r.type === 'income')
    .reduce((sum, r) => sum + parseFloat(r.amount), 0);

  const expense = records
    .filter((r) => r.type === 'expense')
    .reduce((sum, r) => sum + parseFloat(r.amount), 0);

  const net = income - expense;

  return (
    <div>
      <h2 className="text-3xl font-bold mb-8 text-gray-900">Dashboard</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-green-100 p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow">
          <h3 className="text-xl font-semibold">🪙 Total Income</h3>
          <p className="text-3xl font-bold mt-2">${income.toFixed(2)}</p>
        </div>
        <div className="bg-red-100 p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow">
          <h3 className="text-xl font-semibold">🧾 Total Expense</h3>
          <p className="text-3xl font-bold mt-2">${expense.toFixed(2)}</p>
        </div>
        <div className="bg-blue-100 p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow">
          <h3 className="text-xl font-semibold">💼 Net Savings</h3>
          <p className="text-3xl font-bold mt-2">${net.toFixed(2)}</p>
        </div>
      </div>

      <h3 className="text-2xl font-semibold mb-4">Transaction History</h3>
      {loading ? (
        <p className="text-gray-600">Loading...</p>
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white shadow rounded-lg">
            <thead className="bg-gray-200 text-gray-700">
              <tr>
                <th className="p-3 text-left">Date</th>
                <th className="p-3 text-left">Type</th>
                <th className="p-3 text-left">Amount</th>
                <th className="p-3 text-left">Category</th>
                <th className="p-3 text-left">Source</th>
                <th className="p-3 text-left">Vendor</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record, idx) => (
                <tr key={idx} className="border-b hover:bg-gray-50">
                  <td className="p-3">{record.date}</td>
                  <td className="p-3 capitalize">{record.type}</td>
                  <td className="p-3">${parseFloat(record.amount).toFixed(2)}</td>
                  <td className="p-3">{record.category}</td>
                  <td className="p-3">{record.source}</td>
                  <td className="p-3">{record.vendor || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
