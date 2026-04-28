"use client";

import React, { useEffect, useState } from 'react';

export default function Settings() {
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/settings');
        if (res.ok) {
          setSettings(await res.json());
        }
      } catch (error) {
        console.error("Error fetching settings:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  if (loading) {
    return (
      <main className="ml-72 mr-8 pt-8 pb-32 flex justify-center items-center h-screen">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </main>
    );
  }

  return (
    <>
      <main className="ml-72 mr-8 pt-8 pb-32">
        <div className="max-w-[1280px] mx-auto px-container-padding">
          {/* Page Header */}
          <header className="mb-section-margin flex justify-between items-end">
            <div>
              <nav className="flex items-center gap-2 text-slate-400 mb-2">
                <span className="text-label-md font-label-md uppercase tracking-wider">System</span>
                <span className="material-symbols-outlined text-sm">chevron_right</span>
                <span className="text-label-md font-label-md uppercase tracking-wider text-primary">Configuration</span>
              </nav>
              <h2 className="font-headline-lg text-headline-lg text-on-surface">Pipeline Settings</h2>
              <p className="font-body-lg text-body-lg text-on-surface-variant">Configure review ingestion sources, AI parameters, and delivery integrations.</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="font-label-lg text-on-surface">Himanshu</p>
                  <p className="text-[10px] text-slate-400 font-medium">Admin</p>
                </div>
                <div className="w-12 h-12 rounded-full border-2 border-white shadow-md bg-primary flex items-center justify-center text-white font-bold">H</div>
              </div>
            </div>
          </header>

          {/* Settings Grid */}
          <div className="grid grid-cols-12 gap-gutter">
            {/* Section 1: Ingestion Config */}
            <section className="col-span-12 lg:col-span-7 floating-card p-8">
              <div className="flex items-center gap-3 mb-8">
                <span className="material-symbols-outlined text-primary text-2xl">cloud_download</span>
                <h3 className="font-title-lg text-title-lg text-on-surface">Review Ingestion</h3>
              </div>
              <div className="space-y-8">
                {/* Switch Row */}
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-label-lg text-on-surface">Automatic Review Fetching</p>
                    <p className="font-body-md text-on-surface-variant">Automatically fetch new reviews every Monday at 9:00 AM IST.</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input defaultChecked={settings?.ingestion?.realtime_stream} className="sr-only peer" type="checkbox"/>
                    <div className="w-11 h-6 bg-surface-container-highest rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
                {/* Review Sources */}
                <div className="space-y-3">
                  <p className="font-label-lg text-on-surface">Review Data Sources</p>
                  <p className="font-body-md text-on-surface-variant">Select which platforms to scrape app reviews from.</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {settings?.ingestion?.platforms?.map((platform: any, idx: number) => (
                      <span key={idx} className={platform.active 
                        ? "bg-secondary-container text-primary px-4 py-2 rounded-full font-label-md flex items-center gap-2 cursor-pointer hover:bg-primary hover:text-white transition-all"
                        : "bg-surface-container-low text-on-surface-variant px-4 py-2 rounded-full font-label-md hover:bg-surface-variant transition-colors cursor-pointer border border-outline-variant/30"
                      }>
                        {platform.active && <span className="material-symbols-outlined text-sm">check</span>}
                        {platform.name}
                      </span>
                    ))}
                  </div>
                </div>
                {/* Clustering Parameters */}
                <div className="space-y-4">
                  <p className="font-label-lg text-on-surface">AI Clustering Parameters</p>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="font-label-md text-primary ml-1">Min Cluster Size</label>
                      <input className="w-full bg-[#F3F4F9] border-0 rounded-xl px-4 py-3 font-body-md focus:ring-2 focus:ring-primary focus:bg-white transition-all outline-none" type="number" defaultValue={8}/>
                    </div>
                    <div className="space-y-2">
                      <label className="font-label-md text-primary ml-1">Max Themes</label>
                      <input className="w-full bg-[#F3F4F9] border-0 rounded-xl px-4 py-3 font-body-md focus:ring-2 focus:ring-primary focus:bg-white transition-all outline-none" type="number" defaultValue={7}/>
                    </div>
                  </div>
                </div>
                {/* Weeks to Analyze */}
                <div className="space-y-2">
                  <label className="font-label-md text-primary ml-1">Weeks of Review History</label>
                  <input className="w-full bg-[#F3F4F9] border-0 rounded-xl px-4 py-3 font-body-md focus:ring-2 focus:ring-primary focus:bg-white transition-all outline-none" type="number" defaultValue={12} min={1} max={52}/>
                  <p className="font-body-md text-on-surface-variant ml-1">How many weeks of reviews to analyze (1-52).</p>
                </div>
              </div>
            </section>

            {/* Section 2: MCP Integration */}
            <section className="col-span-12 lg:col-span-5 floating-card p-8 h-fit">
              <div className="flex items-center gap-3 mb-8">
                <span className="material-symbols-outlined text-primary text-2xl">hub</span>
                <h3 className="font-title-lg text-title-lg text-on-surface">Google Workspace</h3>
              </div>
              <div className="space-y-6">
                <div className="p-6 bg-surface-container-low rounded-2xl border border-outline-variant/30">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <p className="font-label-lg text-on-surface">MCP Connector</p>
                      <p className="font-body-md text-on-surface-variant">{settings?.mcp_integration?.connector}</p>
                    </div>
                    <span className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full font-label-md">{settings?.mcp_integration?.status}</span>
                  </div>
                  <div className="h-1 bg-surface-container-high rounded-full overflow-hidden">
                    <div className="h-full bg-primary" style={{ width: `${settings?.mcp_integration?.efficiency}%` }}></div>
                  </div>
                  <p className="font-label-md text-on-surface-variant mt-2">{settings?.mcp_integration?.efficiency}% Delivery Success Rate</p>
                </div>

                {/* Google Docs Config */}
                <div className="space-y-3">
                  <p className="font-label-lg text-on-surface">Google Docs Integration</p>
                  <div className="flex items-center gap-3 p-3 bg-surface-container-low rounded-xl">
                    <span className="material-symbols-outlined text-blue-500">description</span>
                    <div className="flex-1">
                      <p className="font-label-md text-on-surface">Weekly Pulse Report Document</p>
                      <p className="text-[11px] text-slate-400 truncate">Reports are appended to shared Google Doc</p>
                    </div>
                    <span className="material-symbols-outlined text-emerald-500 text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-surface-container-low rounded-xl">
                    <span className="material-symbols-outlined text-red-500">mail</span>
                    <div className="flex-1">
                      <p className="font-label-md text-on-surface">Gmail Notification</p>
                      <p className="text-[11px] text-slate-400 truncate">Summary email with doc link</p>
                    </div>
                    <span className="material-symbols-outlined text-emerald-500 text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4">
                  <p className="font-label-lg text-on-surface">PII Scrubbing</p>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input defaultChecked={settings?.mcp_integration?.strict_validation} className="sr-only peer" type="checkbox"/>
                    <div className="w-11 h-6 bg-surface-container-highest rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
                <button className="w-full py-3 rounded-xl font-label-lg text-primary bg-secondary-fixed hover:bg-secondary-fixed-dim transition-colors flex items-center justify-center gap-2">
                  <span className="material-symbols-outlined text-xl">sync</span>
                  Test Google Connection
                </button>
              </div>
            </section>

            {/* Section 3: Environment Details */}
            <section className="col-span-12 lg:col-span-12 floating-card p-8">
              <div className="flex items-center gap-3 mb-8">
                <span className="material-symbols-outlined text-primary text-2xl">terminal</span>
                <h3 className="font-title-lg text-title-lg text-on-surface">Environment & Runtime</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
                <div className="space-y-2">
                  <label className="font-label-md text-on-surface-variant ml-1">Environment</label>
                  <div className="relative">
                    <input className="w-full bg-surface-container-low border-0 rounded-xl px-4 py-3 font-body-md text-on-surface-variant cursor-not-allowed" readOnly type="text" defaultValue={settings?.environment?.name}/>
                    <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-slate-400">lock</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="font-label-md text-on-surface-variant ml-1">Pipeline ID</label>
                  <input className="w-full bg-[#F3F4F9] border-0 rounded-xl px-4 py-3 font-body-md focus:ring-2 focus:ring-primary focus:bg-white transition-all outline-none" type="text" defaultValue={settings?.environment?.cluster_id}/>
                </div>
                <div className="space-y-2">
                  <label className="font-label-md text-on-surface-variant ml-1">Logging Level</label>
                  <select className="w-full bg-[#F3F4F9] border-0 rounded-xl px-4 py-3 font-body-md focus:ring-2 focus:ring-primary focus:bg-white transition-all outline-none appearance-none" defaultValue={settings?.environment?.logging_level}>
                    <option value="Debug">Debug</option>
                    <option value="Information">Information</option>
                    <option value="Warning">Warning</option>
                    <option value="Critical">Critical</option>
                  </select>
                </div>
              </div>
              {/* Tech Stack Display */}
              <div className="mt-8 p-6 bg-surface-container-low rounded-2xl">
                <p className="font-label-md font-bold uppercase tracking-widest text-slate-400 mb-4">Tech Stack</p>
                <div className="flex flex-wrap gap-3">
                  {['Python 3.11', 'FastAPI', 'Gemini 2.5 Flash', 'UMAP + HDBSCAN', 'Sentence-Transformers', 'Google MCP', 'SQLite', 'Next.js'].map((tech) => (
                    <span key={tech} className="px-4 py-2 bg-white rounded-full text-label-md font-bold text-on-surface shadow-sm border border-slate-100">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>

      {/* Floating Save Configurations Action Bar */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 w-full max-w-[600px] z-50 px-4">
        <div className="glass-sidebar shadow-[0px_20px_40px_rgba(103,80,164,0.15)] rounded-full px-8 py-4 flex items-center justify-between gap-4 border border-white/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-50 rounded-full flex items-center justify-center">
              <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>info</span>
            </div>
            <span className="font-label-md text-on-surface hidden sm:block">Unsaved changes detected</span>
          </div>
          <div className="flex items-center gap-3">
            <button className="px-6 py-2.5 rounded-full font-label-lg text-on-surface-variant hover:bg-slate-100 transition-colors">Discard</button>
            <button className="px-8 py-2.5 rounded-full font-label-lg bg-primary text-white shadow-lg hover:shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all">
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
