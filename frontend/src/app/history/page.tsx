"use client";

import React, { useEffect, useState } from 'react';
import { getApiUrl } from '@/lib/api';

export default function History() {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(getApiUrl('/api/reports/weekly'));
        if (res.ok) {
          setReport(await res.json());
        }
      } catch (error) {
        console.error("Error fetching weekly report:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  if (loading) {
    return (
      <main className="ml-72 mr-8 pt-8 pb-12 max-w-[1280px] flex justify-center items-center h-screen">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </main>
    );
  }

  return (
    <>
      <main className="ml-72 mr-8 pt-8 pb-12 max-w-[1280px]">
        {/* Header Section */}
        <header className="flex justify-between items-end mb-10">
          <div>
            <nav className="flex items-center gap-2 text-slate-400 mb-2">
              <span className="text-label-md font-label-md uppercase tracking-wider">Reports</span>
              <span className="material-symbols-outlined text-sm">chevron_right</span>
              <span className="text-label-md font-label-md uppercase tracking-wider text-primary">Weekly Groww Pulse</span>
            </nav>
            <h2 className="font-headline-lg text-headline-lg text-on-surface">{report?.date_range}</h2>
            <p className="text-slate-500 mt-1 font-body-md">AI-powered analysis of {report?.total_feedback?.toLocaleString()} Groww app reviews from Play Store & App Store.</p>
          </div>
          <div className="flex gap-3">
            <button onClick={() => window.print()} className="px-5 py-2.5 rounded-xl border-none bg-secondary-container text-primary font-bold flex items-center gap-2 hover:bg-primary hover:text-white transition-all">
              <span className="material-symbols-outlined text-lg">ios_share</span>
              Export PDF
            </button>
            <button onClick={() => window.open('https://docs.google.com/document/u/0/', '_blank')} className="px-5 py-2.5 rounded-xl border-none bg-secondary-container text-primary font-bold flex items-center gap-2 hover:bg-primary hover:text-white transition-all">
              <span className="material-symbols-outlined text-lg">description</span>
              View in Docs
            </button>
            <button className="p-2.5 rounded-xl bg-white shadow-sm border border-slate-100 text-slate-600">
              <span className="material-symbols-outlined">more_horiz</span>
            </button>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-gutter">
          {/* Left Column: Sentiment & Themes */}
          <div className="col-span-8 flex flex-col gap-gutter">
            {/* Sentiment Breakdown Card */}
            <section className="bg-white rounded-3xl p-container-padding shadow-[0px_10px_30px_rgba(0,0,0,0.04)]">
              <div className="flex justify-between items-start mb-8">
                <div>
                  <h3 className="font-title-lg text-title-lg text-on-surface">Review Sentiment Breakdown</h3>
                  <p className="text-slate-500 text-body-md">Analysis of {report?.total_feedback?.toLocaleString()} user reviews from Groww app</p>
                </div>
                <div className="flex items-center gap-2 bg-secondary-fixed text-primary px-3 py-1 rounded-full text-label-md font-bold">
                  <span className="material-symbols-outlined text-sm">trending_up</span>
                  +8% vs LW
                </div>
              </div>
              <div className="flex items-center justify-around py-4">
                {/* Custom Donut Chart Visualization */}
                <div className="relative w-48 h-48">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" fill="transparent" r="40" stroke="#F3F4F9" strokeWidth="12"></circle>
                    <circle cx="50" cy="50" fill="transparent" r="40" stroke="#4f378a" strokeDasharray="251.2" strokeDashoffset={`${251.2 - (251.2 * report?.sentiment?.positive?.percentage / 100)}`} strokeWidth="12"></circle>
                    <circle cx="50" cy="50" fill="transparent" r="40" stroke="#ffd9e3" strokeDasharray="251.2" strokeDashoffset={`${251.2 - (251.2 * report?.sentiment?.critical?.percentage / 100)}`} strokeWidth="12"></circle>
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-headline-lg font-headline-lg text-on-surface">{report?.sentiment?.positive?.percentage}%</span>
                    <span className="text-label-md text-slate-400 font-bold uppercase tracking-widest">Positive</span>
                  </div>
                </div>
                {/* Legend Items */}
                <div className="flex flex-col gap-4">
                  <div className="flex items-center gap-4">
                    <div className="w-3 h-10 rounded-full bg-primary"></div>
                    <div>
                      <p className="text-label-lg font-label-lg text-on-surface">Positive Reviews</p>
                      <p className="text-body-md text-slate-500">{report?.sentiment?.positive?.count?.toLocaleString()} reviews • {report?.sentiment?.positive?.label}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-3 h-10 rounded-full bg-tertiary-fixed"></div>
                    <div>
                      <p className="text-label-lg font-label-lg text-on-surface">Neutral Reviews</p>
                      <p className="text-body-md text-slate-500">{report?.sentiment?.neutral?.count?.toLocaleString()} reviews • {report?.sentiment?.neutral?.label}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-3 h-10 rounded-full bg-error-container"></div>
                    <div>
                      <p className="text-label-lg font-label-lg text-on-surface">Critical Reviews</p>
                      <p className="text-body-md text-slate-500">{report?.sentiment?.critical?.count?.toLocaleString()} reviews • {report?.sentiment?.critical?.label}</p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Theme Deep Dive Section */}
            <section className="bg-white rounded-3xl p-container-padding shadow-[0px_10px_30px_rgba(0,0,0,0.04)]">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-2xl bg-error-container flex items-center justify-center text-error">
                    <span className="material-symbols-outlined">error_outline</span>
                  </div>
                  <div>
                    <h3 className="font-title-lg text-title-lg text-on-surface">{report?.deep_dive?.theme}</h3>
                    <div className="flex gap-2 items-center">
                      <span className="text-label-md font-bold uppercase tracking-wider text-error">{report?.deep_dive?.status}</span>
                      <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                      <span className="text-body-md text-slate-500">{report?.deep_dive?.impact}</span>
                    </div>
                  </div>
                </div>
                <button className="text-primary font-bold text-label-lg hover:underline underline-offset-4">View All Reviews</button>
              </div>
              <div className="grid grid-cols-2 gap-4 mb-8">
                {report?.deep_dive?.examples?.map((ex: any, idx: number) => (
                  <div key={idx} className="bg-surface-container-lowest p-6 rounded-2xl border-l-4 border-error">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-[10px] font-bold">{ex.user?.charAt(0)}</div>
                      <span className="text-label-md font-bold text-on-surface">{ex.user}</span>
                      <span className="text-slate-400 text-label-md">{ex.time}</span>
                    </div>
                    <p className="text-body-md text-on-surface-variant italic">"{ex.comment}"</p>
                  </div>
                ))}
              </div>
              <div className="p-6 bg-secondary-fixed/30 rounded-2xl flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-primary shadow-sm">
                    <span className="material-symbols-outlined">lightbulb</span>
                  </div>
                  <div>
                    <p className="font-bold text-on-surface">AI Recommended Action</p>
                    <p className="text-body-md text-on-secondary-fixed-variant">{report?.deep_dive?.recommended_action}</p>
                  </div>
                </div>
                <button className="bg-primary text-white px-6 py-2 rounded-xl font-bold text-label-lg shadow-md hover:shadow-lg transition-shadow">Create Ticket</button>
              </div>
            </section>
          </div>

          {/* Right Column: Sidebar Stats & Integrations */}
          <div className="col-span-4 flex flex-col gap-gutter">
            {/* Integration Status Card */}
            <section className="bg-white rounded-3xl p-container-padding shadow-[0px_10px_30px_rgba(0,0,0,0.04)]">
              <h3 className="font-title-lg text-title-lg text-on-surface mb-6">Delivery Status</h3>
              <div className="flex flex-col gap-6">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="w-10 h-10 shrink-0 rounded-xl bg-slate-50 flex items-center justify-center">
                      <span className="material-symbols-outlined text-red-500">mail</span>
                    </div>
                    <div className="min-w-0">
                      <p className="font-bold text-on-surface truncate">Gmail Digest</p>
                      <p className="text-label-md text-slate-400 truncate">Sent to product team</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-green-600 shrink-0">
                    <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                    <span className="text-label-md font-bold uppercase tracking-tighter">Sent</span>
                  </div>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="w-10 h-10 shrink-0 rounded-xl bg-slate-50 flex items-center justify-center">
                      <span className="material-symbols-outlined text-blue-500">description</span>
                    </div>
                    <div className="min-w-0">
                      <p className="font-bold text-on-surface truncate">Google Docs Report</p>
                      <p className="text-label-md text-slate-400 truncate">Appended to Weekly Pulse doc</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-green-600 shrink-0">
                    <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                    <span className="text-label-md font-bold uppercase tracking-tighter">Live</span>
                  </div>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="w-10 h-10 shrink-0 rounded-xl bg-slate-50 flex items-center justify-center">
                      <span className="material-symbols-outlined text-purple-400">storage</span>
                    </div>
                    <div className="min-w-0">
                      <p className="font-bold text-on-surface truncate">Local Backup</p>
                      <p className="text-label-md text-slate-400 truncate">data/summaries/latest_report.md</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-green-600 shrink-0">
                    <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                    <span className="text-label-md font-bold uppercase tracking-tighter">Saved</span>
                  </div>
                </div>
              </div>
              <div className="mt-8 pt-8 border-t border-slate-100">
                <p className="text-label-md font-bold uppercase tracking-widest text-slate-400 mb-4">Next Scheduled Run</p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-primary-fixed flex flex-col items-center justify-center text-primary">
                    <span className="text-label-md font-black">APR</span>
                    <span className="text-title-lg font-black leading-none">28</span>
                  </div>
                  <div>
                    <p className="text-label-lg font-bold text-on-surface">Weekly Pulse Report</p>
                    <p className="text-body-md text-slate-500">Scheduled for Monday 09:00 AM IST</p>
                  </div>
                </div>
              </div>
            </section>

            {/* Quick Stats Card */}
            <section className="bg-white rounded-3xl p-container-padding shadow-[0px_10px_30px_rgba(0,0,0,0.04)]">
              <h3 className="font-title-lg text-title-lg text-on-surface mb-6">Report Highlights</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-4 bg-surface-container-low rounded-xl">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-primary">source</span>
                    <span className="font-label-lg text-on-surface">Data Sources</span>
                  </div>
                  <span className="font-label-lg font-bold text-primary">2 platforms</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-surface-container-low rounded-xl">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-primary">category</span>
                    <span className="font-label-lg text-on-surface">Themes Found</span>
                  </div>
                  <span className="font-label-lg font-bold text-primary">9 clusters</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-surface-container-low rounded-xl">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-primary">timer</span>
                    <span className="font-label-lg text-on-surface">Processing Time</span>
                  </div>
                  <span className="font-label-lg font-bold text-primary">4m 32s</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-surface-container-low rounded-xl">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-primary">security</span>
                    <span className="font-label-lg text-on-surface">PII Scrubbed</span>
                  </div>
                  <span className="font-label-lg font-bold text-primary">31 entries</span>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>
      {/* FAB for quick actions */}
      <button className="fixed bottom-8 right-8 w-16 h-16 bg-primary text-white rounded-2xl shadow-2xl flex items-center justify-center hover:rotate-90 transition-all duration-300 z-50">
        <span className="material-symbols-outlined text-3xl">auto_awesome</span>
      </button>
    </>
  );
}
