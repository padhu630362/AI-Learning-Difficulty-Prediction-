import React, { useEffect } from 'react';
import { AlertTriangle, Info, AlertCircle, X } from 'lucide-react';

const ConfirmDialog = ({
  isOpen,
  title = 'Are you sure?',
  message = 'Please confirm this action.',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'primary', // 'primary' | 'danger' | 'warning'
  isLoading = false,
  onConfirm,
  onCancel,
}) => {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && !isLoading) onCancel();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleEscape);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onCancel, isLoading]);

  if (!isOpen) return null;

  let icon = <Info className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />;
  let iconBg = 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400';
  let buttonStyle = 'bg-emerald-600 hover:bg-emerald-500 text-white';

  if (variant === 'danger') {
    icon = <AlertCircle className="w-6 h-6 text-rose-600 dark:text-rose-400" />;
    iconBg = 'bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400';
    buttonStyle = 'bg-rose-600 hover:bg-rose-700 text-white focus:ring-rose-500';
  } else if (variant === 'warning') {
    icon = <AlertTriangle className="w-6 h-6 text-amber-600 dark:text-amber-400" />;
    iconBg = 'bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400';
    buttonStyle = 'bg-gold-500 hover:bg-gold-600 text-forest-950 font-semibold focus:ring-gold-400';
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4 text-center sm:p-0">
        <div
          className="fixed inset-0 bg-forest-980/60 backdrop-blur-sm transition-opacity"
          onClick={!isLoading ? onCancel : undefined}
        />

        <div className="relative transform overflow-hidden rounded-2xl bg-white dark:bg-forest-900 text-left shadow-2xl transition-all w-full max-w-md my-8 z-10 border border-forest-100 dark:border-forest-800 p-6">
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-xl shrink-0 ${iconBg}`}>
              {icon}
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-forest-900 dark:text-forest-100 leading-6">
                {title}
              </h3>
              <p className="mt-2 text-sm text-forest-600 dark:text-forest-300 leading-relaxed">
                {message}
              </p>
            </div>
          </div>

          <div className="mt-6 flex justify-end gap-3">
            <button
              type="button"
              disabled={isLoading}
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-forest-700 dark:text-forest-200 bg-white dark:bg-forest-800 border border-forest-200 dark:border-forest-700 rounded-xl hover:bg-ivory-100 dark:hover:bg-forest-700 transition-colors disabled:opacity-50"
            >
              {cancelText}
            </button>
            <button
              type="button"
              disabled={isLoading}
              onClick={onConfirm}
              className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors shadow-sm disabled:opacity-50 ${buttonStyle}`}
            >
              {isLoading ? 'Processing...' : confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;

