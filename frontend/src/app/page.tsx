"use client";

import React, { useEffect, useState } from 'react';
import { getApiUrl } from '@/lib/api';

export default function Dashboard() {
  const [health, setHealth] = useState<any>(null);
  const [themes, setThemes] = useState<any[]>([]);
  const [feed, setFeed] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [pipelineStatus, setPipelineStatus] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthRes, themesRes, feedRes, statusRes] = await Promise.all([
          fetch(getApiUrl('/api/dashboard/health')),
          fetch(getApiUrl('/api/dashboard/themes')),
          fetch(getApiUrl('/api/dashboard/feed')),
          fetch(getApiUrl('/api/status'))
        ]);
        
        if (healthRes.ok) setHealth(await healthRes.json());
        if (themesRes.ok) setThemes(await themesRes.json());
        if (feedRes.ok) setFeed(await feedRes.json());
        if (statusRes.ok) setPipelineStatus(await statusRes.json());
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    const interval = setInterval(async () => {
      try {
        const res = await fetch(getApiUrl('/api/status'));
        if (res.ok) setPipelineStatus(await res.json());
      } catch {}
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleGenerateReport = async () => {
    if (pipelineStatus?.is_running) return;
    setIsGenerating(true);
    try {
      const res = await fetch(getApiUrl('/api/generate-report'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product: 'Groww', min_cluster: 20, max_themes: 7 })
      });
      if (res.ok) {
        const statusRes = await fetch(getApiUrl('/api/status'));
        if (statusRes.ok) setPipelineStatus(await statusRes.json());
      }
    } catch (error) {
      console.error("Failed to trigger generation:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  if (loading) {
    return (
      <main className="ml-72 mt-28 px-8 pb-12 max-w-[1280px] flex justify-center items-center h-64">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </main>
    );
  }

  const scoreColor = (health?.score ?? 0) >= 80 ? 'text-emerald-600' : (health?.score ?? 0) >= 60 ? 'text-amber-600' : 'text-error';

  return (
    <>
      {/* TopNavBar */}
      <header className="fixed top-4 left-72 right-4 rounded-2xl z-40 glass-header shadow-[0px_10px_30px_rgba(0,0,0,0.04)] flex justify-between items-center px-8 py-3 max-w-[1280px]">
        <div className="flex items-center gap-4 bg-slate-100/50 px-4 py-2 rounded-full w-96">
          <span className="material-symbols-outlined text-slate-400">search</span>
          <input className="bg-transparent border-none focus:ring-0 text-body-md w-full placeholder:text-slate-400" placeholder="Search reviews, themes, reports..." type="text"/>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <button className="w-10 h-10 rounded-full flex items-center justify-center text-slate-500 hover:bg-slate-50 transition-all relative">
              <span className="material-symbols-outlined">notifications</span>
              <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full"></span>
            </button>
            <button className="w-10 h-10 rounded-full flex items-center justify-center text-slate-500 hover:bg-slate-50 transition-all">
              <span className="material-symbols-outlined">help</span>
            </button>
          </div>
          <div className="h-8 w-[1px] bg-slate-200"></div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="font-label-lg text-on-surface">Himanshu</p>
              <p className="text-[10px] text-slate-400 font-medium">Product Analyst</p>
            </div>
            <div className="w-10 h-10 rounded-full border-2 border-white shadow-sm bg-primary flex items-center justify-center text-white font-bold text-sm">H</div>
          </div>
        </div>
      </header>

      {/* Main Content Canvas */}
      <main className="ml-72 mt-28 px-8 pb-12 max-w-[1280px]">
        {/* Hero Section: Pulse Score */}
        <section className="grid grid-cols-12 gap-gutter mb-section-margin">
          <div className="col-span-12 lg:col-span-8 bg-white floating-card p-container-padding flex items-center justify-between relative overflow-hidden premium-shadow">
            <div className="z-10">
              <div className="flex items-center gap-2 mb-2">
                <span className="material-symbols-outlined text-primary text-sm">insights</span>
                <span className="text-label-md font-bold uppercase tracking-widest text-primary">Groww App Health</span>
              </div>
              <h2 className="font-headline-lg text-on-surface mb-2">Overall Sentiment Score</h2>
              <p className="text-slate-500 font-body-lg mb-8 max-w-md">{health?.message}</p>
              <div className="flex items-end gap-4">
                <div className={`text-[80px] font-extrabold leading-none tracking-tighter ${scoreColor}`}>{health?.score}</div>
                <div className="mb-3">
                  <span className="flex items-center text-emerald-600 font-bold text-lg">
                    <span className="material-symbols-outlined mr-1">trending_{health?.trend_direction}</span>
                    {health?.trend}
                  </span>
                  <p className="text-label-md text-slate-400">{health?.comparison}</p>
                </div>
              </div>
            </div>
            <div className="hidden md:block w-1/2 h-full absolute right-0 top-0 pt-12">
              <svg className="w-full h-full opacity-30 group" viewBox="0 0 400 200">
                <path d="M0,150 Q50,140 100,160 T200,100 T300,120 T400,40" fill="none" stroke="#6750A4" strokeLinecap="round" strokeWidth="6"></path>
                <path d="M0,150 Q50,140 100,160 T200,100 T300,120 T400,40 V200 H0 Z" fill="url(#gradient)" opacity="0.2"></path>
                <defs>
                  <linearGradient id="gradient" x1="0%" x2="0%" y1="0%" y2="100%">
                    <stop offset="0%" style={{ stopColor: '#6750A4', stopOpacity: 1 }}></stop>
                    <stop offset="100%" style={{ stopColor: '#6750A4', stopOpacity: 0 }}></stop>
                  </linearGradient>
                </defs>
                <circle cx="400" cy="40" fill="#6750A4" r="8"></circle>
              </svg>
            </div>
          </div>
          
          {/* Generate Report Action Card */}
          <div className="col-span-12 lg:col-span-4 bg-primary-container text-white floating-card p-container-padding flex flex-col justify-between relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2"></div>
            <div className="z-10">
              <h3 className="font-headline-md mb-2">Weekly Pulse Report</h3>
              <p className="font-body-md opacity-80 mb-4">Analyze {'>'}1,200 Groww reviews with AI clustering and deliver insights to Google Docs.</p>
              
              {/* Pipeline Status Indicator */}
              <div className="flex items-center gap-2 mb-6 bg-white/10 px-3 py-2 rounded-xl">
                {pipelineStatus?.is_running ? (
                  <>
                    <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                    <span className="text-label-md font-bold opacity-90">Pipeline Running...</span>
                  </>
                ) : pipelineStatus?.status_message?.includes('Success') ? (
                  <>
                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                    <span className="text-label-md font-bold opacity-90">Last run: Success ✓</span>
                  </>
                ) : (
                  <>
                    <span className="w-2 h-2 rounded-full bg-white/60"></span>
                    <span className="text-label-md font-bold opacity-90">Ready to generate</span>
                  </>
                )}
              </div>
            </div>
            <button
              onClick={handleGenerateReport}
              disabled={pipelineStatus?.is_running || isGenerating}
              className={`bg-white text-primary px-6 py-3 rounded-xl font-label-lg flex items-center justify-center gap-2 transition-all w-full z-10 ${
                pipelineStatus?.is_running || isGenerating
                  ? 'opacity-70 cursor-not-allowed'
                  : 'hover:bg-slate-50 hover:scale-[1.02] active:scale-[0.98]'
              }`}
            >
              {pipelineStatus?.is_running ? (
                <>
                  <span className="material-symbols-outlined animate-spin text-sm">sync</span>
                  Generating...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined">play_arrow</span>
                  Generate Report
                </>
              )}
            </button>
          </div>
        </section>

        {/* Bento Grid: Top Themes & AI Action Items */}
        <section className="grid grid-cols-12 gap-gutter mb-section-margin">
          {/* Top Themes */}
          <div className="col-span-12 lg:col-span-7">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-headline-md text-on-surface">Trending Review Themes</h3>
              <button className="text-primary font-label-lg flex items-center gap-1 hover:underline">
                View Full Report <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-card-gap">
              {themes.map((theme) => (
                <div key={theme.id} className="bg-white floating-card p-6 flex flex-col gap-4 group hover:scale-[1.02] transition-transform">
                  <div className="flex justify-between items-start">
                    <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
                      theme.trend_type === 'critical' ? 'bg-error-container text-error' : 'bg-secondary-container text-primary'
                    }`}>
                      <span className="material-symbols-outlined">{theme.icon}</span>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-[10px] font-bold ${
                      theme.trend_type === 'critical' ? 'bg-error-container text-on-error-container' : 'bg-emerald-100 text-emerald-700'
                    }`}>{theme.trend}</span>
                  </div>
                  <div>
                    <h4 className="font-title-lg text-on-surface mb-1">{theme.title}</h4>
                    <p className="text-body-md text-slate-500">{theme.description}</p>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="material-symbols-outlined text-sm text-slate-400">group</span>
                    <span className="text-label-md text-slate-400">{theme.users_affected} reviews mentioning this</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          {/* AI Action Items */}
          <div className="col-span-12 lg:col-span-5">
            <div className="bg-white floating-card h-full p-container-padding">
              <div className="flex items-center gap-2 mb-8">
                <span className="material-symbols-outlined text-primary">auto_awesome</span>
                <h3 className="font-headline-md text-on-surface">AI Action Items</h3>
              </div>
              <div className="space-y-6">
                <div className="flex gap-4 p-4 rounded-2xl bg-surface-container-low border border-transparent hover:border-primary/20 transition-colors">
                  <div className="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-error text-white">
                    <span className="material-symbols-outlined text-sm">priority_high</span>
                  </div>
                  <div>
                    <p className="font-label-lg text-on-surface mb-1">Fix KYC Verification Pipeline</p>
                    <p className="text-label-md text-slate-500 mb-2">28% of negative reviews cite KYC delays {'>'} 3 days.</p>
                    <span className="px-2 py-0.5 bg-error-container text-on-error-container text-[10px] font-bold rounded uppercase">High Priority</span>
                  </div>
                </div>
                <div className="flex gap-4 p-4 rounded-2xl bg-surface-container-low border border-transparent hover:border-primary/20 transition-colors">
                  <div className="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-amber-500 text-white">
                    <span className="material-symbols-outlined text-sm">warning</span>
                  </div>
                  <div>
                    <p className="font-label-lg text-on-surface mb-1">Investigate UPI SIP Auto-Debit</p>
                    <p className="text-label-md text-slate-500 mb-2">19% increase in UPI mandate failure complaints.</p>
                    <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-[10px] font-bold rounded uppercase">Medium Priority</span>
                  </div>
                </div>
                <div className="flex gap-4 p-4 rounded-2xl bg-surface-container-low border border-transparent hover:border-primary/20 transition-colors">
                  <div className="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-primary text-white">
                    <span className="material-symbols-outlined text-sm">lightbulb</span>
                  </div>
                  <div>
                    <p className="font-label-lg text-on-surface mb-1">Prioritize Dark Mode Release</p>
                    <p className="text-label-md text-slate-500 mb-2">26% feature requests. High correlation with 5-star reviews.</p>
                    <span className="px-2 py-0.5 bg-secondary-container text-primary text-[10px] font-bold rounded uppercase">Opportunity</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Live Feed Analysis */}
        <section className="grid grid-cols-12 gap-gutter">
          <div className="col-span-12 bg-white floating-card p-container-padding overflow-hidden">
            <div className="flex justify-between items-center mb-8">
              <div>
                <h3 className="font-headline-md text-on-surface">Live Review Feed</h3>
                <p className="text-body-md text-slate-500">Real-time stream of Groww app reviews and AI analysis events.</p>
              </div>
              <div className="flex gap-2">
                <button className="px-4 py-2 bg-primary text-white rounded-xl text-label-md font-bold hover:bg-primary/90 transition-colors flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
                  Live
                </button>
                <button className="px-4 py-2 bg-slate-50 rounded-xl text-label-md font-bold text-slate-600 hover:bg-slate-100">Play Store</button>
                <button className="px-4 py-2 bg-slate-50 rounded-xl text-label-md font-bold text-slate-600 hover:bg-slate-100">App Store</button>
              </div>
            </div>
            <div className="space-y-1">
              {feed.map((item, idx) => {
                let dotColor = "bg-emerald-500 ring-emerald-50";
                if (item.status === "warning") dotColor = "bg-amber-500 ring-amber-50";
                if (item.status === "error") dotColor = "bg-error ring-error-container";

                return (
                  <div key={idx} className={`grid grid-cols-12 gap-4 py-4 px-6 hover:bg-slate-50/50 rounded-2xl transition-all group ${idx !== feed.length - 1 ? 'border-b border-slate-50' : ''}`}>
                    <div className="col-span-1 flex items-center justify-center">
                      <div className={`w-2 h-2 rounded-full ${dotColor} ring-4 shadow-sm`}></div>
                    </div>
                    <div className="col-span-2">
                      <span className="text-label-md font-bold text-slate-400">{item.time}</span>
                    </div>
                    <div className="col-span-6">
                      <p className="text-body-md text-on-surface font-medium">{item.message}</p>
                    </div>
                    <div className="col-span-3 flex justify-end">
                      <div className="flex gap-2">
                        <span className={`px-3 py-1 rounded-full text-[10px] font-bold ${
                          item.tags[1] === 'CRITICAL' ? 'bg-error-container text-on-error-container' :
                          item.tags[1] === 'ALERT' ? 'bg-amber-100 text-amber-700' :
                          item.tags[1] === 'COMPLETE' ? 'bg-emerald-100 text-emerald-700' :
                          item.tags[1] === 'FEATURE' ? 'bg-blue-100 text-blue-700' :
                          'bg-secondary-container text-primary'
                        }`}>{item.tags[0]}</span>
                        <span className={`px-3 py-1 rounded-full text-[10px] font-bold ${
                          item.tags[1] === 'CRITICAL' ? 'bg-red-50 text-red-600' :
                          item.tags[1] === 'ALERT' ? 'bg-amber-50 text-amber-600' :
                          'bg-surface-container text-slate-500'
                        }`}>{item.tags[1]}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      </main>
    </>
  );
}
