import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, NavLink, Outlet } from "react-router";
import { useToast } from "../components/ui/Toast";
import { auth } from "../lib/api";

export function AdminLayout() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const { data: operator } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: auth.me,
  });

  const logoutMut = useMutation({
    mutationFn: auth.logout,
    onSuccess: () => {
      qc.clear();
      window.location.href = "/login";
    },
    onError: () => toast("Logout failed", "error"),
  });

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded text-sm font-medium transition-colors ${
      isActive
        ? "bg-primary text-white"
        : "text-text-secondary hover:text-text-primary hover:bg-surface"
    }`;

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-border">
        <nav
          className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-4"
          aria-label="Admin navigation"
        >
          <Link to="/admin" className="font-semibold text-text-primary mr-4">
            persocart admin
          </Link>
          <NavLink to="/admin/categories" className={navLinkClass}>
            Categories
          </NavLink>
          <NavLink to="/admin/products" className={navLinkClass}>
            Products
          </NavLink>
          <div className="ml-auto flex items-center gap-3">
            <span className="text-sm text-text-secondary">
              {operator?.email}
            </span>
            <button
              type="button"
              onClick={() => logoutMut.mutate()}
              className="cursor-pointer text-sm text-text-secondary hover:text-text-primary px-2 py-1 min-h-[44px]"
            >
              Logout
            </button>
          </div>
        </nav>
      </header>
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
