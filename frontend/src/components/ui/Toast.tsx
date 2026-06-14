import { createContext, useCallback, useContext, useState } from "react";

type ToastLevel = "success" | "error" | "info";

interface ToastItem {
  id: number;
  message: string;
  level: ToastLevel;
}

interface ToastContextValue {
  toast: (message: string, level?: ToastLevel) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

let nextId = 0;

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);

  const toast = useCallback((message: string, level: ToastLevel = "info") => {
    const id = ++nextId;
    setItems((prev) => [...prev, { id, message, level }]);
    setTimeout(() => setItems((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  const bgClass: Record<ToastLevel, string> = {
    success: "bg-success",
    error: "bg-error",
    info: "bg-primary",
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      {/* aria-live polite region for screen readers */}
      <div
        aria-live="polite"
        aria-atomic="false"
        className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm"
      >
        {items.map((t) => (
          <div
            key={t.id}
            role="status"
            className={`${bgClass[t.level]} text-white px-4 py-3 rounded-md shadow-lg text-sm`}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
