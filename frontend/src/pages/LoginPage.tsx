import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Navigate, useNavigate } from "react-router";
import { Button } from "../components/ui/Button";
import { auth } from "../lib/api";
import { ApiError } from "../lib/api-client";

export function LoginPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldError, setFieldError] = useState("");

  const { data: me } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: auth.me,
    retry: false,
  });

  const loginMut = useMutation({
    mutationFn: () => auth.login(email, password),
    onSuccess: (operator) => {
      qc.setQueryData(["auth", "me"], operator);
      navigate("/admin", { replace: true });
    },
    onError: (err) => {
      if (err instanceof ApiError && err.status === 401) {
        setFieldError("Invalid email or password.");
      } else {
        setFieldError("Login failed. Please try again.");
      }
    },
  });

  if (me) return <Navigate to="/admin" replace />;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFieldError("");
    loginMut.mutate();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <div className="w-full max-w-sm bg-white rounded-lg shadow-md p-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-6">
          Operator login
        </h1>
        <form onSubmit={handleSubmit} noValidate aria-label="Login form">
          {fieldError && (
            <div
              role="alert"
              className="mb-4 p-3 bg-red-50 border border-error rounded text-error text-sm"
            >
              {fieldError}
            </div>
          )}
          <div className="mb-4">
            <label
              htmlFor="email"
              className="block text-sm font-medium text-text-primary mb-1"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus-ring min-h-[44px]"
            />
          </div>
          <div className="mb-6">
            <label
              htmlFor="password"
              className="block text-sm font-medium text-text-primary mb-1"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus-ring min-h-[44px]"
            />
          </div>
          <Button
            type="submit"
            variant="primary"
            disabled={loginMut.isPending}
            className="w-full justify-center"
          >
            {loginMut.isPending ? "Signing in…" : "Sign in"}
          </Button>
        </form>
      </div>
    </div>
  );
}
