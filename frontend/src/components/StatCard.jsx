import React from 'react';

const StatCard = ({ title, value, subtitle, icon: Icon, color = 'emerald', trend }) => {
  const colorMap = {
    emerald: 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800',
    gold: 'bg-gold-50 dark:bg-gold-950/60 text-gold-600 dark:text-gold-400 border-gold-200 dark:border-gold-800',
    forest: 'bg-forest-100 dark:bg-forest-900 text-forest-700 dark:text-forest-300 border-forest-300 dark:border-forest-700',
    amber: 'bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-800',
    rose: 'bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 border-rose-200 dark:border-rose-800',
    blue: 'bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800',
    purple: 'bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-800',
    indigo: 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800',
  };

  return (
    <div className="bg-white dark:bg-forest-950 rounded-2xl border border-forest-200/80 dark:border-forest-800/80 p-5 shadow-xs hover:shadow-md transition-all">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-wider text-forest-500 dark:text-forest-400">{title}</p>
          <p className="text-2xl font-bold font-serif text-forest-900 dark:text-forest-100 mt-1">{value}</p>
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl border ${colorMap[color] || colorMap.emerald}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      {(subtitle || trend) && (
        <div className="mt-3 flex items-center text-xs text-forest-500 dark:text-forest-400">
          {trend && (
            <span className={`font-semibold mr-1.5 ${trend > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
              {trend > 0 ? `+${trend}%` : `${trend}%`}
            </span>
          )}
          <span>{subtitle}</span>
        </div>
      )}
    </div>
  );
};

export default StatCard;
