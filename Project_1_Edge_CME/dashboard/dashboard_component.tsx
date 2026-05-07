import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Settings, Calculator, Activity, ShieldAlert, Zap } from 'lucide-react';

const ResearcherDashboard = () => {
    const [zThreshold, setZThreshold] = useState(3.5);
    const [data, setData] = useState([]);
    const [formula, setFormula] = useState('\\text{Severity} = \\frac{\\Delta \\text{Flux} \\cdot \\text{Confidence}}{\\text{Baseline Noise}}');

    // Simulate Data Streaming
    useEffect(() => {
        const generateData = () => {
            let base = 100;
            return Array.from({ length: 40 }, (_, i) => {
                const flux = base + Math.random() * 20 + (i > 30 ? 60 : 0);
                return {
                    time: `${i}:00`,
                    flux: flux,
                    z: (flux - 100) / 10,
                    threshold: zThreshold
                };
            });
        };
        setData(generateData());
    }, [zThreshold]);

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
            <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                        Solar Edge AI: CME Intelligence
                    </h1>
                    <p className="text-slate-400">Project 1: Edge CME | SWIS-ASPEX Multivariate Detection</p>
                </div>
                <div className="flex gap-4">
                    <div className="bg-slate-900 px-4 py-2 rounded-lg border border-slate-800 flex items-center gap-2">
                        <Activity size={18} className="text-green-400" />
                        <span className="text-sm font-medium">Edge Status: Operational</span>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-12 gap-6">
                {/* Left Panel: Tuning & Formulas */}
                <div className="col-span-4 space-y-6">
                    {/* Parameter Tuning */}
                    <section className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-xl">
                        <div className="flex items-center gap-2 mb-4">
                            <Settings className="text-blue-400" size={20} />
                            <h2 className="text-xl font-semibold">Live Parameter Tuning</h2>
                        </div>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">Dynamic Z-Score Threshold: {zThreshold}</label>
                                <input 
                                    type="range" min="1" max="10" step="0.1" 
                                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                                    value={zThreshold}
                                    onChange={(e) => setZThreshold(parseFloat(e.target.value))}
                                />
                            </div>
                            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                                <p className="text-xs text-blue-300">
                                    Current Sensitivity optimized for **CEF0.5 Score** (High Precision).
                                </p>
                            </div>
                        </div>
                    </section>

                    {/* Formula Sandbox */}
                    <section className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-xl">
                        <div className="flex items-center gap-2 mb-4">
                            <Calculator className="text-cyan-400" size={20} />
                            <h2 className="text-xl font-semibold">Formula Sandbox</h2>
                        </div>
                        <div className="space-y-4">
                            <p className="text-xs text-slate-400 italic">Scientific notation support (LaTeX):</p>
                            <textarea 
                                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm font-mono text-cyan-300 focus:ring-1 focus:ring-cyan-500 outline-none"
                                rows="3"
                                value={formula}
                                onChange={(e) => setFormula(e.target.value)}
                            />
                            <div className="p-2 bg-slate-950/50 border border-slate-800 rounded text-center">
                                <span className="text-sm text-slate-300">Preview: {formula}</span>
                            </div>
                            <button className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 rounded-lg font-medium transition-colors">
                                Re-Calculate Dataset
                            </button>
                        </div>
                    </section>
                </div>

                {/* Right Panel: Data Visualization */}
                <div className="col-span-8 space-y-6">
                    <section className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-xl h-[500px]">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-semibold flex items-center gap-2">
                                <Zap className="text-yellow-400" size={20} />
                                Multi-Channel Ion Flux Analysis
                            </h2>
                            <div className="flex gap-2">
                                <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-400">99.2% Accuracy</span>
                                <span className="text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded border border-red-500/30 font-bold animate-pulse">
                                    CME DETECTED
                                </span>
                            </div>
                        </div>
                        
                        <div className="h-[380px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={data}>
                                    <defs>
                                        <linearGradient id="colorFlux" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                    <XAxis dataKey="time" stroke="#64748b" fontSize={12} />
                                    <YAxis stroke="#64748b" fontSize={12} />
                                    <Tooltip 
                                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                                        itemStyle={{ color: '#f1f5f9' }}
                                    />
                                    <Area type="monotone" dataKey="flux" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorFlux)" />
                                    <Line type="monotone" dataKey="threshold" stroke="#ef4444" strokeDasharray="5 5" strokeWidth={2} dot={false} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="mt-4 flex justify-center gap-6 text-xs text-slate-500">
                            <span className="flex items-center gap-1"><span className="w-3 h-3 bg-blue-500 rounded-full"></span> Proton Flux (n/cm²/s)</span>
                            <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-red-500 border-t border-dashed"></span> Dynamic Threshold</span>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
};

export default ResearcherDashboard;
