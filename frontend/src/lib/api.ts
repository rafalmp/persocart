import { apiFetch } from "./api-client";

// ------------------------------------------------------------------ types

export interface Operator {
  id: number;
  email: string;
  isStaff: boolean;
  dateJoined: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  parent: number | null;
  level: number;
  createdAt: string;
  updatedAt: string;
}

export interface CategoryNode {
  id: number;
  name: string;
  slug: string;
  children: CategoryNode[];
}

export interface Product {
  id: number;
  category: number;
  name: string;
  slug: string;
  description: string;
  price: string;
  imageUrl: string | null;
  alt_text: string;
  isActive: boolean;
  filterValues: ProductFilterValue[];
  createdAt: string;
  updatedAt: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export type FilterType = "choice" | "multichoice" | "number" | "boolean";

export interface FilterOption {
  id: number;
  label: string;
  value: string;
  position: number;
}

export interface CategoryFilter {
  id: number;
  category: number;
  name: string;
  slug: string;
  type: FilterType;
  unit: string;
  position: number;
  options: FilterOption[];
}

export interface ProductFilterValue {
  id: number;
  filter: number;
  option: number | null;
  valueNumber: string | null;
  valueBoolean: boolean | null;
}

export interface ProductFilterValueWrite {
  filter: number;
  option?: number | null;
  valueNumber?: string | null;
  valueBoolean?: boolean | null;
}

// ------------------------------------------------------------------ auth

export const auth = {
  me: () => apiFetch<Operator>("/auth/me"),
  login: (email: string, password: string) =>
    apiFetch<Operator>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  logout: () => apiFetch<null>("/auth/logout", { method: "POST" }),
};

// ------------------------------------------------------------------ categories (admin)

export const categories = {
  list: () => apiFetch<Paginated<Category>>("/categories"),
  tree: () => apiFetch<CategoryNode[]>("/categories/tree"),
  get: (id: number) => apiFetch<Category>(`/categories/${id}`),
  create: (data: { name: string; parent?: number | null }) =>
    apiFetch<Category>("/categories", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: { name: string; parent?: number | null }) =>
    apiFetch<Category>(`/categories/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  remove: (id: number) =>
    apiFetch<null>(`/categories/${id}`, { method: "DELETE" }),
  filters: (id: number) =>
    apiFetch<CategoryFilter[]>(`/categories/${id}/filters`),
};

// ------------------------------------------------------------------ products (admin)

export const products = {
  list: (params?: { category?: number; page?: number }) => {
    const qs = new URLSearchParams();
    if (params?.category) qs.set("category", String(params.category));
    if (params?.page) qs.set("page", String(params.page));
    return apiFetch<Paginated<Product>>(`/products${qs.size ? `?${qs}` : ""}`);
  },
  get: (id: number) => apiFetch<Product>(`/products/${id}`),
  create: (data: FormData) =>
    apiFetch<Product>("/products", { method: "POST", body: data }),
  update: (id: number, data: FormData) =>
    apiFetch<Product>(`/products/${id}`, { method: "PUT", body: data }),
  remove: (id: number) =>
    apiFetch<null>(`/products/${id}`, { method: "DELETE" }),
  setFilterValues: (id: number, values: ProductFilterValueWrite[]) =>
    apiFetch<ProductFilterValue[]>(`/products/${id}/filter-values`, {
      method: "PUT",
      body: JSON.stringify(values),
    }),
};

// ------------------------------------------------------------------ filters (admin)

export const filters = {
  createForCategory: (
    categoryId: number,
    data: {
      name: string;
      type: FilterType;
      unit?: string;
      position?: number;
      options?: { label: string; value: string; position?: number }[];
    },
  ) =>
    apiFetch<CategoryFilter>(`/categories/${categoryId}/filters`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (
    id: number,
    data: Partial<Omit<CategoryFilter, "id" | "category" | "slug">>,
  ) =>
    apiFetch<CategoryFilter>(`/filters/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  remove: (id: number) =>
    apiFetch<null>(`/filters/${id}`, { method: "DELETE" }),
};

// ------------------------------------------------------------------ storefront (public)

export const storefront = {
  categories: () => apiFetch<CategoryNode[]>("/storefront/categories"),
  categoryFilters: (slug: string) =>
    apiFetch<CategoryFilter[]>(`/storefront/categories/${slug}/filters`),
  categoryProducts: (
    slug: string,
    params?: Record<string, string | string[]>,
  ) => {
    const qs = new URLSearchParams();
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        if (Array.isArray(v)) {
          for (const val of v) qs.append(k, val);
        } else {
          qs.set(k, v);
        }
      }
    }
    return apiFetch<Paginated<Product>>(
      `/storefront/categories/${slug}/products${qs.size ? `?${qs}` : ""}`,
    );
  },
  product: (slug: string) => apiFetch<Product>(`/storefront/products/${slug}`),
};
