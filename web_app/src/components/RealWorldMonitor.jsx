import React, { useState, useEffect } from 'react';
import realWorldData from '../real_world_data.json';

const RealWorldMonitor = () => {
    const [data, setData] = useState([]);

    useEffect(() => {
        // Sort data by severity: High > Medium > Low > Safe
        const severityOrder = {
            'high': 4,
            'medium': 3,
            'low': 2,
            'safe': 1,
            'unknown': 0
        };

        const sortedData = [...realWorldData]
            .filter(item => item.severity?.toLowerCase() !== 'unknown') // Filter out unknown severity
            .sort((a, b) => {
                const sevA = severityOrder[a.severity?.toLowerCase()] || 0;
                const sevB = severityOrder[b.severity?.toLowerCase()] || 0;
                return sevB - sevA; // Descending order
            });

        setData(sortedData);
    }, []);

    if (!data || data.length === 0) {
        return <div className="monitor-empty">No real-world data collected yet. Run the fetch script.</div>;
    }

    return (
        <div className="monitor-container">
            <h2>🌍 Real World Monitor</h2>
            <p>Live feed of reported incidents and discussions from the web, analyzed for severity.</p>

            <div className="monitor-grid">
                {data.map((item, index) => (
                    <div key={index} className={`monitor-card severity-${item.severity.toLowerCase()}`}>
                        <div className="monitor-header">
                            <span className="timestamp">{item.timestamp}</span>
                            <span className={`severity-badge ${item.severity.toLowerCase()}`}>
                                {item.severity.toUpperCase()} SEVERITY
                            </span>
                        </div>
                        <h3><a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a></h3>
                        <p className="monitor-content">{item.content}</p>
                        <div className="monitor-footer">
                            <span className="category-tag">Detected: {item.detected_category}</span>
                            <p className="reason"><strong>Analysis:</strong> {item.reason}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RealWorldMonitor;
