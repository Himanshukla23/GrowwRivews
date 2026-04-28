import React from 'react';
import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  trend?: string;
  trendUp?: boolean;
  icon: LucideIcon;
  className?: string;
}

export function StatCard({ title, value, trend, trendUp, icon: Icon, className }: StatCardProps) {
  return (
    <div className={cn("bg-white p-6 rounded-2xl border border-gray-100 shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)] flex flex-col gap-4 transition-transform hover:-translate-y-1 hover:shadow-[0_8px_20px_-4px_rgba(0,0,0,0.08)]", className)}>
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center text-gray-500">
          <Icon className="w-5 h-5" />
        </div>
        <span className="text-gray-500 font-medium text-sm">{title}</span>
      </div>
      
      <div className="flex items-end justify-between">
        <h3 className="text-3xl font-bold text-gray-900">{value}</h3>
        {trend && (
          <div className={cn("flex items-center gap-1 text-sm font-medium px-2 py-1 rounded-full", trendUp ? "text-emerald-700 bg-emerald-50" : "text-rose-700 bg-rose-50")}>
            {trendUp ? '↑' : '↓'} {trend}
          </div>
        )}
      </div>
    </div>
  );
}
