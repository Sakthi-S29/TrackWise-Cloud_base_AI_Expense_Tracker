import React, { useState } from 'react';

function AddEntry() {
  const [entryType, setEntryType] = useState('income');
  const [amount, setAmount] = useState('');
  const [year, setYear] = useState('');
  const [month, setMonth] = useState('');
  const [day, setDay] = useState('');
  const [description, setDescription] = useState('');
  const [vendor, setVendor] = useState('');
  const [error, setError] = useState('');
  const [billFile, setBillFile] = useState(null);
  const [parsedItems, setParsedItems] = useState([]);
  const [category, setCategory] = useState('');

  const years = Array.from({ length: 100 }, (_, i) => 2025 - i);
  const months = Array.from({ length: 12 }, (_, i) => i + 1);
  const days = Array.from({ length: 31 }, (_, i) => i + 1);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!amount) {
      setError('Amount is required');
      return;
    }
    if (!year || !month || !day) {
      setError('Complete date is required');
      return;
    }
    if (!description.trim()) {
      setError('Description is required');
      return;
    }

    setError('');
    const fullDate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const payload = {
      type: entryType,
      amount: parseFloat(amount),
      date: fullDate,
      category,
      description,
      vendor
    };

    try {
      const response = await fetch("https://faleg426z1.execute-api.us-east-1.amazonaws.com/manual-entry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      if (response.ok) {
        alert("Entry submitted successfully!");
        setAmount('');
        setYear('');
        setMonth('');
        setDay('');
        setCategory('');
        setDescription('');
        setVendor('');
      } else {
        setError(result.error || "Submission failed.");
      }
    } catch (err) {
      console.error("Submit failed:", err);
      setError("Something went wrong.");
    }
  };

  const handleBillUpload = (e) => {
    const file = e.target.files[0];
    setBillFile(file);
    console.log('Bill file selected:', file);
    setParsedItems([
      { item: 'Milk 1L', amount: 60, category: 'Food' },
      { item: 'Dettol', amount: 150, category: 'Health' }
    ]);
  };

  const handleParsedChange = (index, field, value) => {
    const updated = [...parsedItems];
    updated[index][field] = value;
    setParsedItems(updated);
  };

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6 text-gray-900">Add {entryType === 'income' ? 'Income' : 'Expense'}</h2>
      <div className="mb-6 flex gap-4">
        <button
          className={`px-6 py-2 text-white rounded-lg font-medium ${entryType === 'income' ? 'bg-green-600' : 'bg-gray-300'}`}
          onClick={() => setEntryType('income')}
        >Income</button>
        <button
          className={`px-6 py-2 text-white rounded-lg font-medium ${entryType === 'expense' ? 'bg-red-600' : 'bg-gray-300'}`}
          onClick={() => setEntryType('expense')}
        >Expense</button>
      </div>

      {entryType === 'expense' && (
        <>
          <div className="text-md font-medium text-gray-700 mb-2">Track expense manually or upload a bill for AI-based parsing:</div>
          <div className="bg-gray-50 p-4 rounded-lg shadow-sm mb-6">
            <h3 className="text-lg font-semibold mb-2">Option 1: Upload Expense Bill</h3>
            <input
              type="file"
              accept=".pdf,image/*"
              onChange={handleBillUpload}
              className="w-full p-3 border rounded-lg"
            />
            {billFile && <p className="mt-2 text-green-600">Selected file: {billFile.name}</p>}
            {parsedItems.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold mb-2">Parsed Items</h4>
                <table className="table-auto w-full text-left border">
                  <thead>
                    <tr className="bg-gray-200">
                      <th className="p-2 border">Item</th>
                      <th className="p-2 border">Amount</th>
                      <th className="p-2 border">Category</th>
                    </tr>
                  </thead>
                  <tbody>
                    {parsedItems.map((item, i) => (
                      <tr key={i}>
                        <td className="p-2 border">{item.item}</td>
                        <td className="p-2 border">{item.amount}</td>
                        <td className="p-2 border">
                          <select
                            value={item.category}
                            onChange={(e) => handleParsedChange(i, 'category', e.target.value)}
                            className="border rounded p-1"
                          >
                            <option>Food</option>
                            <option>Health</option>
                            <option>Travel</option>
                            <option>Utilities</option>
                            <option>Other</option>
                          </select>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
          <div className="text-center font-medium text-gray-500 my-4">OR</div>
        </>
      )}

      <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow-md max-w-xl">
        {error && <div className="text-red-600 font-medium">{error}</div>}
        <input
          type="number"
          placeholder="Amount"
          className="w-full p-3 border rounded-lg"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <div className="flex gap-4">
          <select className="w-1/3 p-3 border rounded-lg" value={year} onChange={(e) => setYear(e.target.value)}>
            <option value="">Year</option>
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
          <select className="w-1/3 p-3 border rounded-lg" value={month} onChange={(e) => setMonth(e.target.value)}>
            <option value="">Month</option>
            {months.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
          <select className="w-1/3 p-3 border rounded-lg" value={day} onChange={(e) => setDay(e.target.value)}>
            <option value="">Day</option>
            {days.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>
        <select
          className="w-full p-3 border rounded-lg"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {entryType === 'income' ? (
            <>
              <option value="">Select Income Category</option>
              <option value="Salary">Salary</option>
              <option value="Gift">Gift</option>
              <option value="Freelance">Freelance</option>
              <option value="Investment">Investment</option>
              <option value="Other">Other</option>
            </>
          ) : (
            <>
              <option value="">Select Expense Category</option>
              <option value="Food">Food</option>
              <option value="Health">Health</option>
              <option value="Travel">Travel</option>
              <option value="Utilities">Utilities</option>
              <option value="Other">Other</option>
            </>
          )}
        </select>
        <input
          type="text"
          placeholder="Description"
          className="w-full p-3 border rounded-lg"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <input
          type="text"
          placeholder="Vendor/Store (optional)"
          className="w-full p-3 border rounded-lg"
          value={vendor}
          onChange={(e) => setVendor(e.target.value)}
        />
        <button type="submit" className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition">Submit</button>
      </form>
    </div>
  );
}

export default AddEntry;
