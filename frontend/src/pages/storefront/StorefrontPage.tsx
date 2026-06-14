import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router";
import { CategoryNav } from "../../components/storefront/CategoryNav";
import { FilterPanel } from "../../components/storefront/FilterPanel";
import { type Product, storefront } from "../../lib/api";

function resolveFilterParams(
  activeFilters: Record<string, string | string[]>,
): Record<string, string | string[]> {
  const params: Record<string, string | string[]> = {};
  for (const [slug, val] of Object.entries(activeFilters)) {
    if (Array.isArray(val)) {
      params[slug] = val;
    } else if (typeof val === "string" && val.startsWith("min:")) {
      params[`${slug}_min`] = val.slice(4);
    } else if (typeof val === "string" && val.startsWith("max:")) {
      params[`${slug}_max`] = val.slice(4);
    } else {
      params[slug] = val;
    }
  }
  return params;
}

export function CategoryPage() {
  const { slug } = useParams<{ slug: string }>();
  const [activeFilters, setActiveFilters] = useState<
    Record<string, string | string[]>
  >({});

  const filterParams = resolveFilterParams(activeFilters);

  const {
    data: productList,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["storefront", "products", slug, filterParams],
    queryFn: () => storefront.categoryProducts(slug!, filterParams),
    enabled: !!slug,
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      {/* Left column: category nav */}
      <aside className="md:col-span-1">
        <CategoryNav />
      </aside>

      {/* Main content */}
      <div className="md:col-span-3">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters */}
          {slug && (
            <div className="lg:col-span-1">
              <FilterPanel
                categorySlug={slug}
                activeFilters={activeFilters}
                onChange={setActiveFilters}
              />
            </div>
          )}

          {/* Product grid */}
          <section
            aria-label="Products"
            className={slug ? "lg:col-span-3" : "lg:col-span-4"}
          >
            {!slug && (
              <div className="text-center py-16 text-text-secondary">
                <p className="text-lg">Select a category to browse products.</p>
              </div>
            )}
            {isLoading && (
              <p className="text-text-secondary text-sm">Loading products…</p>
            )}
            {isError && (
              <p role="alert" className="text-error text-sm">
                Failed to load products.
              </p>
            )}
            {productList && productList.count === 0 && (
              <div className="text-center py-12 text-text-secondary">
                <p>No products found.</p>
                {Object.keys(activeFilters).length > 0 && (
                  <button
                    type="button"
                    onClick={() => setActiveFilters({})}
                    className="mt-2 text-primary hover:underline text-sm min-h-[44px]"
                  >
                    Clear filters
                  </button>
                )}
              </div>
            )}
            {productList && productList.count > 0 && (
              <>
                <p className="text-sm text-text-secondary mb-3">
                  {productList.count} product
                  {productList.count !== 1 ? "s" : ""}
                </p>
                <ul className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                  {productList.results.map((p: Product) => (
                    <li key={p.id}>
                      <Link
                        to={`/product/${p.slug}`}
                        className="block border border-border rounded-lg overflow-hidden hover:shadow-md transition-shadow"
                      >
                        {p.imageUrl ? (
                          <img
                            src={p.imageUrl}
                            alt={p.alt_text || p.name}
                            className="w-full h-40 object-cover"
                            loading="lazy"
                          />
                        ) : (
                          <div className="w-full h-40 bg-surface flex items-center justify-center text-text-secondary text-sm">
                            No image
                          </div>
                        )}
                        <div className="p-3">
                          <h3 className="font-medium text-text-primary text-sm">
                            {p.name}
                          </h3>
                          <p className="text-primary font-semibold mt-1">
                            €{p.price}
                          </p>
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

export function StorefrontHomePage() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      <aside className="md:col-span-1">
        <CategoryNav />
      </aside>
      <div className="md:col-span-3 text-center py-16 text-text-secondary">
        <p className="text-lg">Select a category to browse products.</p>
      </div>
    </div>
  );
}
