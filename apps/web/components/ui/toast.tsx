"use client";

import { create } from "zustand";
import { useEffect } from "react";

type ToastType = "success" | "error" | "info";

interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastStore {
  toasts: Toast[];
  addToast: (type: ToastType, message: string) => void;
  removeToast: (id: string) => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  addToast: (type, message) => {
    const id = Math.random().toString(36).slice(2);
    set((s) => ({ toasts: [...s.toasts, { id, type, message }] }));
    if (type !== "error") {
      setTimeout(() => {
        set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
      }, 5000);
    }
  },
  removeToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));

const iconMap: Record<ToastType, string> = {
  success: "✓",
  error: "✕",
  info: "ℹ",
};

const colorMap: Record<ToastType, string> = {
  success: "border-emerald-800 bg-emerald-950 text-emerald-300",
  error: "border-red-800 bg-red-950 text-red-300",
  info: "border-blue-800 bg-blue-950 text-blue-300",
};

export function ToastContainer() {
  const toasts = useToastStore((s) => s.toasts);
  const removeToast = useToastStore((s) => s.removeToast);

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm" aria-live="polite">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`flex items-center gap-3 px-4 py-3 rounded-lg border shadow-md text-sm ${colorMap[toast.type]}`}
          role="alert"
        >
          <span className="font-bold flex-shrink-0">{iconMap[toast.type]}</span>
          <span className="flex-1">{toast.message}</span>
          <button
            onClick={() => removeToast(toast.id)}
            className="text-current opacity-60 hover:opacity-100 font-bold flex-shrink-0"
            aria-label="Dismiss"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}

/** Shorthand for calling toast from any component */
export function toast(type: ToastType, message: string) {
  useToastStore.getState().addToast(type, message);
}
