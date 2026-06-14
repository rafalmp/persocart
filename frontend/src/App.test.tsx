import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { ToastProvider } from "./components/ui/Toast";
import { StorefrontHomePage } from "./pages/storefront/StorefrontPage";

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider
      client={
        new QueryClient({ defaultOptions: { queries: { retry: false } } })
      }
    >
      <ToastProvider>
        <MemoryRouter>{children}</MemoryRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
}

test("renders storefront home with category prompt", () => {
  render(<StorefrontHomePage />, { wrapper });
  expect(screen.getByText(/select a category/i)).toBeInTheDocument();
});
