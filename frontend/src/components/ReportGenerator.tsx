"use client";

import React, { useState, useEffect } from 'react';
import { Play, Loader2, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

export function ReportGenerator() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/status');
      if (res.ok) {
        const data = await res.json();
        setStatus(data);
      }
    } catch (error) {
      console.error("Failed to fetch status:", error);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000); // Poll every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const handleGenerate = async () => {
    if (status?.is_running) return;
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product: 'Groww', min_cluster: 20, max_themes: 7 })
      });
      if (res.ok) {
        await fetchStatus();
      }
    } catch (error) {
      console.error("Failed to trigger generation:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-3xl p-8 border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] mt-8">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Generate Weekly Pulse Report</h2>
          <p className="text-gray-500 max-w-xl text-sm leading-relaxed">
            Our AI instantly analyzes patterns across thousands of app reviews, clusters them into distinct themes, and suggests actionable insights ready for your executive team.
          </p>
        </div>
        
        <button
          onClick={handleGenerate}
          disabled={status?.is_running || loading}
          className={cn(
            "group relative px-8 py-4 bg-gray-900 text-white rounded-2xl font-semibold shadow-lg shadow-gray-900/20 transition-all flex items-center gap-3 overflow-hidden",
            (status?.is_running || loading) ? "opacity-90 cursor-not-allowed" : "hover:shadow-xl hover:shadow-gray-900/30 hover:-translate-y-0.5 active:translate-y-0"
          )}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]" />
          
          {status?.is_running ? (
            <RefreshCw className="w-5 h-5 animate-spin" />
          ) : (
            <Play className="w-5 h-5 fill-white" />
          )}
          <span>{status?.is_running ? 'Generating...' : 'Generate Now'}</span>
        </button>
      </div>

      <div className="mt-8 pt-8 border-t border-gray-100 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0">
            <RefreshCw className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-1">Status</h4>
            <div className="flex items-center gap-2 text-sm">
              {status?.is_running ? (
                <><Loader2 className="w-4 h-4 animate-spin text-blue-600" /><span className="text-blue-600 font-medium">Running</span></>
              ) : status?.status_message?.includes('Success') ? (
                <><CheckCircle2 className="w-4 h-4 text-emerald-600" /><span className="text-emerald-600 font-medium">Completed</span></>
              ) : status?.status_message?.includes('Failed') || status?.status_message?.includes('Error') ? (
                <><AlertCircle className="w-4 h-4 text-rose-600" /><span className="text-rose-600 font-medium">Failed</span></>
              ) : (
                <span className="text-gray-500">Ready</span>
              )}
            </div>
          </div>
        </div>

        <div className="col-span-2 flex items-start gap-4">
          <div className="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center flex-shrink-0">
            <Loader2 className="w-5 h-5 text-gray-400" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-1">System Logs</h4>
            <p className="text-sm text-gray-600 font-mono bg-gray-50 px-3 py-2 rounded-lg border border-gray-100">
              {status?.status_message || "Awaiting execution..."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
