import React from 'react';

export const CardSkeleton = () => (
  <div className="bg-white rounded-xl border border-slate-200 p-5 animate-pulse">
    <div className="flex justify-between items-center">
      <div className="space-y-2">
        <div className="h-4 bg-slate-200 rounded w-24"></div>
        <div className="h-7 bg-slate-200 rounded w-16"></div>
      </div>
      <div className="h-10 w-10 bg-slate-200 rounded-lg"></div>
    </div>
    <div className="mt-4 h-3 bg-slate-200 rounded w-32"></div>
  </div>
);

export const TableSkeleton = ({ rows = 5 }) => (
  <div className="bg-white rounded-xl border border-slate-200 overflow-hidden animate-pulse">
    <div className="h-12 bg-slate-100 border-b border-slate-200"></div>
    <div className="divide-y divide-slate-100">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="px-6 py-4 flex space-x-4">
          <div className="h-4 bg-slate-200 rounded w-1/4"></div>
          <div className="h-4 bg-slate-200 rounded w-1/4"></div>
          <div className="h-4 bg-slate-200 rounded w-1/4"></div>
          <div className="h-4 bg-slate-200 rounded w-1/4"></div>
        </div>
      ))}
    </div>
  </div>
);

export const ChartSkeleton = () => (
  <div className="bg-white rounded-xl border border-slate-200 p-6 animate-pulse">
    <div className="h-5 bg-slate-200 rounded w-48 mb-6"></div>
    <div className="h-64 bg-slate-100 rounded-lg flex items-end p-4 space-x-3">
      <div className="h-3/4 bg-slate-200 rounded-t w-1/6"></div>
      <div className="h-1/2 bg-slate-200 rounded-t w-1/6"></div>
      <div className="h-5/6 bg-slate-200 rounded-t w-1/6"></div>
      <div className="h-2/3 bg-slate-200 rounded-t w-1/6"></div>
      <div className="h-4/5 bg-slate-200 rounded-t w-1/6"></div>
      <div className="h-1/3 bg-slate-200 rounded-t w-1/6"></div>
    </div>
  </div>
);

export default CardSkeleton;

