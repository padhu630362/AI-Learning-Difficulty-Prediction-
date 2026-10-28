import React, { useEffect } from 'react';
import { X } from 'lucide-react';

const Modal = ({ isOpen, onClose, title, children, maxWidth = 'max-w-xl' }) => {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleEscape);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4 text-center sm:p-0">
        <div
          className="fixed inset-0 bg-forest-980/60 backdrop-blur-sm transition-opacity"
          onClick={onClose}
        />

        <div className={`relative transform overflow-hidden rounded-2xl bg-white dark:bg-forest-900 text-left shadow-2xl transition-all w-full ${maxWidth} my-8 z-10 border border-forest-100 dark:border-forest-800`}>
          <div className="flex items-center justify-between border-b border-forest-100 dark:border-forest-800/80 px-6 py-4 bg-ivory-50/50 dark:bg-forest-950/40">
            <h3 className="text-lg font-semibold text-forest-900 dark:text-forest-100">{title}</h3>
            <button
              onClick={onClose}
              className="rounded-lg p-1.5 text-forest-400 dark:text-forest-400 hover:bg-forest-100 dark:hover:bg-forest-800 hover:text-forest-700 dark:hover:text-forest-200 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="px-6 py-5 max-h-[calc(85vh-100px)] overflow-y-auto text-forest-800 dark:text-forest-200">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal;

