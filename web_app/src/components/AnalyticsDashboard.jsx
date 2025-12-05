import React, { useMemo } from 'react';
import {
    PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
    BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import './AnalyticsDashboard.css';

const AnalyticsDashboard = ({ data }) => {
    const stats = useMemo(() => {
        const severityCounts = { High: 0, Medium: 0, Low: 0, Safe: 0, Unknown: 0 };
        const categoryCounts = {};

        data.forEach(item => {
            // Severity
            const sev = item.severity ? item.severity.charAt(0).toUpperCase() + item.severity.slice(1).toLowerCase() : 'Unknown';
            if (severityCounts[sev] !== undefined) {
                severityCounts[sev]++;
            } else {
                severityCounts['Unknown']++;
            }

            // Category
            const cat = item.detected_category || 'Unknown';
            categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
        });

        const severityData = Object.keys(severityCounts).map(key => ({
            name: key,
            value: severityCounts[key]
        })).filter(item => item.value > 0);

        const categoryData = Object.keys(categoryCounts).map(key => ({
            name: key,
            value: categoryCounts[key]
        })).sort((a, b) => b.value - a.value);

        return { severityData, categoryData };
    }, [data]);

    const COLORS = {
        High: '#ef4444',
        Medium: '#f97316',
        Low: '#eab308',
        Safe: '#22c55e',
        Unknown: '#94a3b8'
    };

    return (
        <div className="analytics-container">
            <h2>📊 Data Analytics</h2>
            <p>Real-time analysis of collected safety incidents.</p>

            <div className="charts-grid">
                <div className="chart-card">
                    <h3>Severity Distribution</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={stats.severityData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {stats.severityData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[entry.name] || COLORS.Unknown} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="chart-card">
                    <h3>Category Breakdown</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={stats.categoryData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis type="number" />
                                <YAxis dataKey="name" type="category" width={100} />
                                <Tooltip />
                                <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="stats-summary">
                <div className="stat-box">
                    <h4>Total Incidents</h4>
                    <span className="stat-value">{data.length}</span>
                </div>
                <div className="stat-box">
                    <h4>High Severity</h4>
                    <span className="stat-value danger">{stats.severityData.find(d => d.name === 'High')?.value || 0}</span>
                </div>
                <div className="stat-box">
                    <h4>Top Category</h4>
                    <span className="stat-value">{stats.categoryData[0]?.name || 'N/A'}</span>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsDashboard;
