import React, { useEffect, useState } from 'react';
import { ArrowDownCircle, ArrowUpCircle } from 'lucide-react';

function Dashboard() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/get-transactions`);
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

  const filteredRecords = records.filter((r) => {
    return (
      (filter === 'all' || r.type === filter) &&
      r.vendor?.toLowerCase().includes(search.toLowerCase())
    );
  });

  const income = records
    .filter((r) => r.type === 'income')
    .reduce((sum, r) => sum + parseFloat(r.amount), 0);

  const expense = records
    .filter((r) => r.type === 'expense')
    .reduce((sum, r) => sum + parseFloat(r.amount), 0);

  const net = income - expense;

  const downloadCSV = () => {
    const csvContent = [
      ['Date', 'Type', 'Amount', 'Category', 'Source', 'Vendor'],
      ...records.map((r) => [r.date, r.type, r.amount, r.category, r.source, r.vendor || '-']),
    ]
      .map((row) => row.join(','))
      .join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'trackwise_transactions.csv';
    link.click();
  };

  return (
    <div>
      <h2 className="text-3xl font-bold mb-8 text-gray-900">Dashboard</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-green-100 p-6 rounded-2xl shadow-md">
          <h3 className="text-xl font-semibold">🪙 Total Income</h3>
          <p className="text-3xl font-bold mt-2 text-green-800">${income.toFixed(2)}</p>
        </div>
        <div className="bg-red-100 p-6 rounded-2xl shadow-md">
          <h3 className="text-xl font-semibold">🧾 Total Expense</h3>
          <p className="text-3xl font-bold mt-2 text-red-800">${expense.toFixed(2)}</p>
        </div>
        <div className="bg-blue-100 p-6 rounded-2xl shadow-md">
          <h3 className="text-xl font-semibold">💼 Net Savings</h3>
          <p className="text-3xl font-bold mt-2 text-blue-800">${net.toFixed(2)}</p>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between mb-4 gap-2">
        <div className="space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 rounded-full border ${filter === 'all' ? 'bg-gray-800 text-white' : 'bg-white'} transition`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('income')}
            className={`px-3 py-1 rounded-full border ${filter === 'income' ? 'bg-green-600 text-white' : 'bg-white'} transition`}
          >
            Income
          </button>
          <button
            onClick={() => setFilter('expense')}
            className={`px-3 py-1 rounded-full border ${filter === 'expense' ? 'bg-red-600 text-white' : 'bg-white'} transition`}
          >
            Expense
          </button>
        </div>
        <input
          type="text"
          placeholder="Search by vendor"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border px-3 py-2 rounded-lg shadow-sm focus:outline-none focus:ring"
        />
        <button
          onClick={downloadCSV}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 shadow"
        >
          ⬇️ Export CSV
        </button>
      </div>

      <h3 className="text-2xl font-semibold mb-3">Transaction History</h3>
      {loading ? (
        <p className="text-gray-500">Loading transactions...</p>
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : filteredRecords.length === 0 ? (
        <p className="text-gray-600 italic">No matching records found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white rounded-lg shadow">
            <thead className="bg-gray-100 text-gray-700">
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
              {filteredRecords.map((record, idx) => (
                <tr
                  key={idx}
                  className={`border-b hover:bg-gray-50 ${
                    record.type === 'income' ? 'text-green-700' : 'text-red-700'
                  }`}
                >
                  <td className="p-3">{record.date}</td>
                  <td className="p-3 capitalize">
                    {record.type === 'income' ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-100">
                        <ArrowDownCircle className="h-4 w-4" />
                        Income
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-100">
                        <ArrowUpCircle className="h-4 w-4" />
                        Expense
                      </span>
                    )}
                  </td>
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
