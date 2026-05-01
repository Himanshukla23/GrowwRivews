"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { getApiUrl } from '@/lib/api';

export function Sidebar() {
  const pathname = usePathname();
  const [isRunning, setIsRunning] = useState(false);

  const fetchStatus = async () => {
    try {
      const res = await fetch(getApiUrl('/api/status'));
      if (res.ok) {
        const data = await res.json();
        setIsRunning(data.is_running);
      }
    } catch {}
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleRunPipeline = async () => {
    if (isRunning) return;
    setIsRunning(true);
    try {
      await fetch(getApiUrl('/api/generate-report'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product: 'Groww', min_cluster: 10, max_themes: 7 })
      });
      fetchStatus();
    } catch (error) {
      console.error("Failed to run pipeline:", error);
      setIsRunning(false);
    }
  };

  const navItems = [
    { name: 'Dashboard', icon: 'dashboard', href: '/' },
    { name: 'Pipeline', icon: 'account_tree', href: '/pipeline' },
    { name: 'Reports', icon: 'assessment', href: '/history' },
    { name: 'Settings', icon: 'settings', href: '/settings' },
  ];

  return (
    <aside className="fixed left-4 top-4 bottom-4 w-64 rounded-3xl z-50 glass-sidebar shadow-[0px_20px_40px_rgba(103,80,164,0.08)] flex flex-col p-6 gap-8 font-['Plus_Jakarta_Sans'] font-medium overflow-y-auto">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-white shadow-lg">
          <span className="material-symbols-outlined">insights</span>
        </div>
        <div>
          <h1 className="text-lg font-black text-purple-700 leading-none">Groww Pulse</h1>
          <p className="text-[10px] text-slate-500 uppercase tracking-widest mt-1 font-bold">Review Intelligence</p>
        </div>
      </div>
      
      <nav className="flex flex-col gap-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/' && pathname?.startsWith(item.href));
          return (
            <Link 
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                isActive 
                  ? 'bg-purple-50 text-purple-700 font-semibold translate-x-1' 
                  : 'text-slate-500 hover:bg-purple-50/50 hover:text-purple-600'
              }`}
            >
              <span className="material-symbols-outlined group-hover:scale-110 transition-transform">{item.icon}</span>
              <span className="font-label-lg">{item.name}</span>
              {isActive && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-primary"></span>}
            </Link>
          );
        })}
      </nav>

      {/* Quick Stats */}
      <div className="bg-surface-container-low rounded-2xl p-4 space-y-3">
        <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">This Week</p>
        <div className="flex justify-between items-center">
          <span className="text-label-md text-slate-500">Reviews Analyzed</span>
          <span className="text-label-lg font-bold text-primary">1,247</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-label-md text-slate-500">Themes Found</span>
          <span className="text-label-lg font-bold text-primary">9</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-label-md text-slate-500">Avg Rating</span>
          <span className="text-label-lg font-bold text-amber-500">3.8 ★</span>
        </div>
      </div>
      
      <div className="mt-auto">
        <button 
          onClick={handleRunPipeline}
          disabled={isRunning}
          className={`w-full py-4 rounded-2xl font-label-lg flex items-center justify-center gap-2 shadow-lg transition-transform ${
            isRunning 
              ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
              : 'bg-primary text-white shadow-primary/20 hover:scale-[1.02] active:scale-[0.98]'
          }`}
        >
          <span className={`material-symbols-outlined text-sm ${isRunning ? 'animate-spin' : ''}`}>
            {isRunning ? 'sync' : 'play_arrow'}
          </span>
          {isRunning ? 'Generating...' : 'Run Pipeline'}
        </button>
      </div>
    </aside>
  );
}
