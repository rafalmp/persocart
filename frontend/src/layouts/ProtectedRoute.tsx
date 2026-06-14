import { useQuery } from "@tanstack/react-query";
import { Navigate } from "react-router";
import { auth } from "../lib/api";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: auth.me,
    retry: false,
  });

  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        aria-busy="true"
      >
        <span className="text-text-secondary">Loading…</span>
      </div>
    );
  }

  if (error || !data) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
