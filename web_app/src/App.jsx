import React, { useState, useEffect } from 'react';
import { GoogleGenerativeAI } from "@google/generative-ai";
import HelplineBanner from './components/HelplineBanner';
import benchmarkData from './benchmark.json';
import './App.css';
import RealWorldMonitor from './components/RealWorldMonitor';
import './components/RealWorldMonitor.css';

// Initialize Gemini API
// NOTE: In a production app, never hardcode keys on the client.
const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const genAI = new GoogleGenerativeAI(API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-flash-latest" });

function App() {
  const [activeTab, setActiveTab] = useState('dataset');
  const [inputText, setInputText] = useState('');
  const [classificationResult, setClassificationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all');

  const categories = [...new Set(benchmarkData.map(item => item.label))];

  const handleClassify = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setClassificationResult(null);

    try {
      const prompt = `
        Analyze the following text for safety risks related to self-harm, suicide, violence, abuse, or overdose.
        
        Text: "${inputText}"
        
        Return a JSON object with:
        - is_sensitive: boolean
        - category: string (one of the 5 categories or "safe")
        - confidence: string (low/medium/high)
        - explanation: short string
        
        JSON:
      `;

      const result = await model.generateContent(prompt);
      const response = await result.response;
      const text = response.text().replace(/\`\`\`json/g, '').replace(/\`\`\`/g, '').trim();
      setClassificationResult(JSON.parse(text));
    } catch (error) {
      console.error("Error classifying:", error);
      setClassificationResult({ error: `Failed to classify text: ${error.message || error}` });
    } finally {
      setLoading(false);
    }
  };

  const filteredData = filter === 'all'
    ? benchmarkData
    : benchmarkData.filter(item => item.label === filter);

  return (
    <div className="app-container">
      <HelplineBanner />

      <header className="app-header">
        <h1>ParallelGem Safety Benchmark</h1>
        <p>Synthetic dataset generation & detection demo</p>
      </header>

      <div className="tabs">
        <button
          className={activeTab === 'dataset' ? 'active' : ''}
          onClick={() => setActiveTab('dataset')}
        >
          Explore Dataset
        </button>
        <button
          className={activeTab === 'monitor' ? 'active' : ''}
          onClick={() => setActiveTab('monitor')}
        >
          Real World Monitor
        </button>
        <button
          className={activeTab === 'test' ? 'active' : ''}
          onClick={() => setActiveTab('test')}
        >
          Test Your Text
        </button>
      </div>

      <main className="app-content">
        {activeTab === 'dataset' && (
          <div className="dataset-view">
            <div className="filters">
              <label>Filter by Category:</label>
              <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                <option value="all">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            <div className="data-grid">
              {filteredData.map((item, index) => (
                <div key={index} className={`data-card ${item.is_sensitive ? 'sensitive' : 'safe'}`}>
                  <div className="card-header">
                    <span className="badge">{item.label}</span>
                    <span className="source">{item.source}</span>
                  </div>
                  <p className="card-text">"{item.text}"</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'monitor' && <RealWorldMonitor />}

        {activeTab === 'test' && (
          <div className="test-view">
            <h2>Safety Classifier Demo</h2>
            <p>Enter text to check if it gets flagged by Gemini.</p>

            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type something here..."
              rows={5}
            />

            <button onClick={handleClassify} disabled={loading}>
              {loading ? 'Analyzing...' : 'Analyze Text'}
            </button>

            {classificationResult && (
              <div className={`result-box ${classificationResult.is_sensitive ? 'danger' : 'success'}`}>
                {classificationResult.error ? (
                  <p className="error">{classificationResult.error}</p>
                ) : (
                  <>
                    <h3>Result: {classificationResult.is_sensitive ? '⚠️ Sensitive' : '✅ Safe'}</h3>
                    <p><strong>Category:</strong> {classificationResult.category}</p>
                    <p><strong>Confidence:</strong> {classificationResult.confidence}</p>
                    <p><strong>Explanation:</strong> {classificationResult.explanation}</p>
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
