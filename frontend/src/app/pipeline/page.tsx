"use client";

import React, { useEffect, useState } from 'react';

export default function Pipeline() {
  const [health, setHealth] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthRes, logsRes] = await Promise.all([
          fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/pipeline/health`),
          fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/pipeline/logs` )
        ]);
        
        if (healthRes.ok) setHealth(await healthRes.json());
        if (logsRes.ok) setLogs(await logsRes.json());
      } catch (error) {
        console.error("Error fetching pipeline data:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      const [healthRes, logsRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/pipeline/health`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/pipeline/logs` )
      ]);
      if (healthRes.ok) setHealth(await healthRes.json());
      if (logsRes.ok) setLogs(await logsRes.json());
    } catch {} finally {
      setLoading(false);
    }
  };

  const handleStopPipeline = async () => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/stop-pipeline`, { method: 'POST' });
      handleRefresh();
    } catch (error) {
      console.error("Failed to stop pipeline:", error);
    }
  };

  if (loading) {
    return (
      <main className="ml-72 mr-8 py-8 min-h-screen flex justify-center items-center">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </main>
    );
  }

  return (
    <main className="ml-72 mr-8 py-8 min-h-screen">
      <div className="max-w-[1280px] mx-auto space-y-gutter">
        {/* Header Section */}
        <header className="flex justify-between items-end mb-8">
          <div>
            <nav className="flex items-center gap-2 text-slate-400 mb-2">
              <span className="text-label-md font-label-md uppercase tracking-wider">System</span>
              <span className="material-symbols-outlined text-sm">chevron_right</span>
              <span className="text-label-md font-label-md uppercase tracking-wider text-primary">Pipeline Monitor</span>
            </nav>
            <h2 className="font-headline-lg text-on-surface">Review Analysis Pipeline</h2>
            <p className="text-on-surface-variant font-body-md">Monitoring Groww app review ingestion, clustering, and AI summarization.</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full premium-shadow">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="font-label-md text-emerald-600">Pipeline Active</span>
            </div>
            <button className="w-10 h-10 rounded-full bg-white flex items-center justify-center premium-shadow hover:bg-slate-50 transition-colors">
              <span className="material-symbols-outlined text-on-surface-variant">refresh</span>
            </button>
          </div>
        </header>

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-12 gap-gutter">
          {/* Pipeline Overview (Central Focus) */}
          <section className="col-span-12 lg:col-span-8 bg-white rounded-[24px] p-8 premium-shadow relative overflow-hidden">
            <div className="flex justify-between items-start mb-12">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full font-label-md">ACTIVE PIPELINE</span>
                  <span className="font-label-md text-on-surface-variant">Groww Weekly Pulse</span>
                </div>
                <h3 className="font-headline-md text-on-surface">Orchestrator Status</h3>
              </div>
              <div className="text-right">
                <span className="text-4xl font-black text-primary font-display-lg">{health?.orchestrator_status}</span>
                <p className="font-label-md text-emerald-500 flex items-center justify-end gap-1">
                  <span className="material-symbols-outlined text-sm">trending_up</span>
                  Uptime: {health?.uptime}
                </p>
              </div>
            </div>

            {/* Pipeline Flow Visualization */}
            <div className="relative h-64 w-full">
              <div className="absolute inset-0 flex items-end justify-between px-2">
                {/* Visual bars representing review processing volume */}
                <div className="w-1 bg-primary/10 h-[30%] rounded-full"></div>
                <div className="w-1 bg-primary/15 h-[35%] rounded-full"></div>
                <div className="w-1 bg-primary/20 h-[45%] rounded-full"></div>
                <div className="w-1 bg-primary/25 h-[50%] rounded-full"></div>
                <div className="w-1 bg-primary/30 h-[60%] rounded-full"></div>
                <div className="w-1 bg-primary/35 h-[55%] rounded-full"></div>
                <div className="w-1 bg-primary/40 h-[70%] rounded-full"></div>
                <div className="w-1 bg-primary/45 h-[65%] rounded-full"></div>
                <div className="w-1 bg-primary/50 h-[75%] rounded-full"></div>
                <div className="w-1 bg-primary/60 h-[85%] rounded-full"></div>
                <div className="w-1 bg-primary h-[95%] rounded-full shadow-[0_0_15px_rgba(103,80,164,0.4)]"></div>
              </div>
              <svg className="absolute inset-0 h-full w-full" preserveAspectRatio="none" viewBox="0 0 100 100">
                <path d="M0,80 Q10,75 20,70 T40,55 T60,45 T80,35 T100,20" fill="none" stroke="#6750A4" strokeWidth="2" vectorEffect="non-scaling-stroke"></path>
                <path d="M0,80 Q10,75 20,70 T40,55 T60,45 T80,35 T100,20 L100,100 L0,100 Z" fill="url(#gradient-pipeline)" opacity="0.1" vectorEffect="non-scaling-stroke"></path>
                <defs>
                  <linearGradient id="gradient-pipeline" x1="0%" x2="0%" y1="0%" y2="100%">
                    <stop offset="0%" style={{ stopColor: '#6750A4', stopOpacity: 1 }}></stop>
                    <stop offset="100%" style={{ stopColor: '#6750A4', stopOpacity: 0 }}></stop>
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute bottom-0 left-0 right-0 flex justify-between font-label-md text-on-surface-variant pt-4 border-t border-slate-100">
                <span>Week 1</span>
                <span>Week 4</span>
                <span>Week 8</span>
                <span>Week 10</span>
                <span>Week 12</span>
              </div>
            </div>
          </section>

          {/* Resource Stats (Side Stats) */}
          <div className="col-span-12 lg:col-span-4 flex flex-col gap-gutter">
            <div className="bg-white rounded-[24px] p-6 premium-shadow flex-1 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-4">
                <span className="material-symbols-outlined text-primary p-2 bg-purple-50 rounded-lg">reviews</span>
                <span className="font-label-md text-emerald-500 bg-emerald-50 px-2 py-1 rounded">Active</span>
              </div>
              <div>
                <h4 className="font-label-lg text-on-surface-variant uppercase tracking-wider">Reviews Processed</h4>
                <p className="text-4xl font-bold font-headline-lg">1,247</p>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full mt-4 overflow-hidden">
                <div className="bg-primary h-full rounded-full" style={{ width: '100%' }}></div>
              </div>
            </div>
            <div className="bg-white rounded-[24px] p-6 premium-shadow flex-1 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-4">
                <span className="material-symbols-outlined text-tertiary p-2 bg-pink-50 rounded-lg">hub</span>
                <span className="font-label-md text-amber-500 bg-amber-50 px-2 py-1 rounded">Clustering</span>
              </div>
              <div>
                <h4 className="font-label-lg text-on-surface-variant uppercase tracking-wider">Clusters Found</h4>
                <p className="text-4xl font-bold font-headline-lg">9</p>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full mt-4 overflow-hidden">
                <div className="bg-tertiary h-full rounded-full" style={{ width: '72%' }}></div>
              </div>
            </div>
          </div>

          {/* Module Progress Timeline */}
          <section className="col-span-12 lg:col-span-6 bg-white rounded-[24px] p-8 premium-shadow">
            <h3 className="font-headline-md text-on-surface mb-8">Pipeline Modules</h3>
            <div className="space-y-8 relative">
              {/* Connecting Line */}
              <div className="absolute left-[19px] top-4 bottom-4 w-0.5 bg-slate-100"></div>
              
              {health?.modules?.map((mod: any, idx: number) => {
                let icon = "check";
                let colorClass = "bg-emerald-500 text-white";
                let textClass = "text-emerald-500";
                
                if (mod.progress > 0 && mod.progress < 100) {
                  icon = "sync";
                  colorClass = "bg-primary text-white border-4 border-white shadow-lg";
                  textClass = "text-primary";
                } else if (mod.progress === 0) {
                  icon = "schedule";
                  colorClass = "bg-slate-200 text-slate-400";
                  textClass = "text-slate-400";
                }

                return (
                  <div key={idx} className="flex gap-6 relative">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center z-10 ${colorClass}`}>
                      <span className={`material-symbols-outlined ${mod.progress > 0 && mod.progress < 100 ? 'animate-spin' : ''}`}>{icon}</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <h4 className={`font-title-lg ${mod.progress === 0 ? 'opacity-50 text-on-surface' : 'text-on-surface'}`}>{mod.name}</h4>
                        <span className={`font-label-md font-bold ${textClass}`}>{mod.status}</span>
                      </div>
                      <p className={`font-body-md mb-3 ${mod.progress === 0 ? 'text-on-surface-variant opacity-50' : 'text-on-surface-variant'}`}>{mod.message}</p>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div className={`h-full ${mod.progress === 100 ? 'bg-emerald-500' : mod.progress > 0 ? 'bg-primary shadow-[0_0_8px_rgba(103,80,164,0.4)]' : 'bg-slate-300'}`} style={{ width: `${mod.progress}%` }}></div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          {/* Audit Log Stream */}
          <section className="col-span-12 lg:col-span-6 bg-white rounded-[24px] p-8 premium-shadow flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-headline-md text-on-surface">Processing Log</h3>
              <button className="text-primary font-label-lg hover:underline">View Full Log</button>
            </div>
            <div className="space-y-4 flex-1 overflow-y-auto max-h-[400px] pr-2">
              {logs.map((log: any, idx: number) => {
                let icon = "verified_user";
                let bgClass = "bg-emerald-100 text-emerald-700";
                let iconClass = "text-emerald-500 bg-emerald-100";
                
                if (log.level === "INFO") {
                  icon = "info";
                  bgClass = "bg-blue-100 text-blue-700";
                  iconClass = "text-blue-500 bg-blue-100";
                } else if (log.level === "WARNING") {
                  icon = "warning";
                  bgClass = "bg-amber-100 text-amber-700";
                  iconClass = "text-amber-500 bg-amber-100";
                }

                return (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-100 flex items-start gap-4">
                    <span className={`material-symbols-outlined p-2 rounded-xl ${iconClass}`}>{icon}</span>
                    <div className="flex-1">
                      <div className="flex justify-between items-center mb-1">
                        <span className={`px-2 py-0.5 rounded-md font-label-md ${bgClass}`}>{log.level}</span>
                        <span className="text-on-surface-variant font-label-md">{log.time}</span>
                      </div>
                      <p className="text-on-surface font-body-md">{log.message}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </div>

        {/* Footer Details */}
        <footer className="mt-8 pt-8 border-t border-slate-200 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-6">
            <div className="flex flex-col">
              <span className="font-label-md text-on-surface-variant">Pipeline Version</span>
              <span className="font-label-lg font-bold">1.0.0-stable</span>
            </div>
            <div className="flex flex-col">
              <span className="font-label-md text-on-surface-variant">Region</span>
              <span className="font-label-lg font-bold">India-Mumbai</span>
            </div>
            <div className="flex flex-col">
              <span className="font-label-md text-on-surface-variant">AI Model</span>
              <span className="font-label-lg font-bold">Gemini 2.5 Flash</span>
            </div>
          </div>
          <div className="flex gap-4">
            <button className="px-6 py-2 rounded-xl bg-secondary-container text-primary font-label-lg hover:bg-slate-200 transition-colors">Export Pipeline Report</button>
            <button onClick={handleStopPipeline} className="px-6 py-2 rounded-xl bg-error text-white font-label-lg hover:opacity-90 transition-opacity">Stop Pipeline</button>
          </div>
        </footer>
      </div>
    </main>
  );
}
