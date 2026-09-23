import React from 'react';
import { useApp } from '../context/AppContext';

const Toast = () => {
  const { toast } = useApp();

  if (!toast) return null;

  const isSuccess = toast.type === 'success';
  const isError = toast.type === 'error';

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-in fade-in slide-in-from-bottom-4 duration-200 max-w-md">
      <div
        className={`flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg border ${
          isSuccess
            ? 'bg-surface-container-lowest border-tertiary text-on-surface'
            : isError
            ? 'bg-error-container border-error text-on-error-container'
            : 'bg-surface-container-lowest border-primary text-on-surface'
        }`}
      >
        <span
          className={`material-symbols-outlined text-[22px] ${
            isSuccess ? 'text-tertiary' : isError ? 'text-error' : 'text-primary'
          }`}
        >
          {isSuccess ? 'check_circle' : isError ? 'error' : 'info'}
        </span>
        <p className="font-body-md text-body-md leading-snug">{toast.message}</p>
      </div>
    </div>
  );
};

export default Toast;
