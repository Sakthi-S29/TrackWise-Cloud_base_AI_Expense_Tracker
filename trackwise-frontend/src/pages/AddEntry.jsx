import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import 'react-toastify/dist/ReactToastify.css';
import { ToastContainer, toast } from 'react-toastify';


function AddEntry() {
  const [entryType, setEntryType] = useState('income');
  const [amount, setAmount] = useState('');
  const [date, setDate] = useState(new Date());
  const [description, setDescription] = useState('');
  const [vendor, setVendor] = useState('');
  const [category, setCategory] = useState('');
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [billFile, setBillFile] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!amount) return setError('Amount is required');
    if (!description.trim()) return setError('Description is required');
    if (!category) return setError('Category is required');

    setError('');
    const fullDate = date.toISOString().split('T')[0];
    const payload = {
      type: entryType,
      amount: parseFloat(amount),
      date: fullDate,
      category,
      description,
      vendor
    };

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/manual-entry`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      if (response.ok) {
        toast.success("Entry submitted successfully!");
        setAmount('');
        setDate(new Date());
        setCategory('');
        setDescription('');
        setVendor('');
        setError('');
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
  };

 const handleBillUploadSubmit = async () => {
  if (!billFile) {
    setError("Please upload a bill.");
    return;
  }

  setError('');
  setUploading(true);

  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/get-presigned-url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename: billFile.name })
    });

    const { url, fields } = await res.json();

    const uploadData = new FormData();
    Object.entries(fields).forEach(([k, v]) => uploadData.append(k, v));
    uploadData.append("Content-Type", billFile.type);
    uploadData.append("file", billFile);

    const uploadRes = await fetch(url, {
      method: "POST",
      body: uploadData
    });

    if (uploadRes.ok) {
      toast.success("✅ Bill uploaded successfully! Parsing will happen automatically.");
      setBillFile(null);
    } else {
      throw new Error("Upload failed");
    }
  } catch (err) {
    console.error("Upload failed:", err);
    toast.error("❌ Bill upload failed.");
  } finally {
    setUploading(false);
  }
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
            {billFile && (
              <>
                <p className="mt-2 text-green-600">Selected file: {billFile.name}</p>
                <button
                  onClick={handleBillUploadSubmit}
                  className="mt-3 bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700"
                >
                  Upload Bill
                </button>

              </>
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

        <DatePicker
          selected={date}
          onChange={(newDate) => setDate(newDate)}
          className="w-full p-3 border rounded-lg"
          dateFormat="yyyy-MM-dd"
        />

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

        <button
          type="submit"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
        >Submit</button>
      </form>
      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
}

export default AddEntry;
