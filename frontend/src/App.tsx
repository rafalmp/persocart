import { createBrowserRouter, Navigate, RouterProvider } from "react-router";
import { ErrorBoundary } from "./components/ui/ErrorBoundary";
import { ToastProvider } from "./components/ui/Toast";
import { AdminLayout } from "./layouts/AdminLayout";
import { ProtectedRoute } from "./layouts/ProtectedRoute";
import { StorefrontLayout } from "./layouts/StorefrontLayout";
import { CategoriesPage } from "./pages/admin/CategoriesPage";
import { ProductsPage } from "./pages/admin/ProductsPage";
import { LoginPage } from "./pages/LoginPage";
import { ProductDetailPage } from "./pages/storefront/ProductDetailPage";
import {
  CategoryPage,
  StorefrontHomePage,
} from "./pages/storefront/StorefrontPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <StorefrontLayout />,
    errorElement: (
      <ErrorBoundary>
        <div />
      </ErrorBoundary>
    ),
    children: [
      { index: true, element: <StorefrontHomePage /> },
      { path: "category/:slug", element: <CategoryPage /> },
      { path: "product/:slug", element: <ProductDetailPage /> },
    ],
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/admin",
    element: (
      <ProtectedRoute>
        <AdminLayout />
      </ProtectedRoute>
    ),
    errorElement: (
      <ErrorBoundary>
        <div />
      </ErrorBoundary>
    ),
    children: [
      { index: true, element: <Navigate to="/admin/categories" replace /> },
      { path: "categories", element: <CategoriesPage /> },
      { path: "products", element: <ProductsPage /> },
    ],
  },
]);

export function App() {
  return (
    <ToastProvider>
      <RouterProvider router={router} />
    </ToastProvider>
  );
}
