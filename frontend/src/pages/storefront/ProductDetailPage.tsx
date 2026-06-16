import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import { type ProductFilterValue, storefront } from "../../lib/api";

export function ProductDetailPage() {
  const { slug } = useParams<{ slug: string }>();

  const {
    data: product,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["storefront", "product", slug],
    queryFn: () => storefront.product(slug ?? ""),
    enabled: !!slug,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16" aria-busy="true">
        <span className="text-text-secondary">Loading…</span>
      </div>
    );
  }

  if (isError || !product) {
    return (
      <div role="alert" className="text-center py-16">
        <p className="text-error">Product not found.</p>
        <Link
          to="/"
          className="text-primary hover:underline text-sm mt-2 inline-block"
        >
          Back to store
        </Link>
      </div>
    );
  }

  return (
    <article className="max-w-4xl mx-auto">
      <nav aria-label="Breadcrumb" className="mb-6">
        <Link to="/" className="text-primary hover:underline text-sm">
          ← Back to store
        </Link>
      </nav>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Image */}
        <div>
          {product.imageUrl ? (
            <img
              src={product.imageUrl}
              alt={product.alt_text || product.name}
              className="w-full rounded-lg object-cover max-h-96"
            />
          ) : (
            <div className="w-full h-64 bg-surface rounded-lg flex items-center justify-center text-text-secondary">
              No image
            </div>
          )}
        </div>

        {/* Details */}
        <div>
          <h1 className="text-2xl font-semibold text-text-primary mb-2">
            {product.name}
          </h1>
          <p className="text-3xl font-bold text-primary mb-4">
            €{product.price}
          </p>

          {product.description && (
            <p className="text-text-secondary mb-6 leading-relaxed">
              {product.description}
            </p>
          )}

          {/* Filter values */}
          {product.filterValues.length > 0 && (
            <section
              aria-label="Product attributes"
              className="border-t border-border pt-4"
            >
              <h2 className="font-medium text-text-primary mb-3 text-sm uppercase tracking-wide">
                Details
              </h2>
              <FilterValues values={product.filterValues} />
            </section>
          )}
        </div>
      </div>
    </article>
  );
}

function FilterValues({ values }: { values: ProductFilterValue[] }) {
  const grouped = values.reduce<Record<number, ProductFilterValue[]>>(
    (acc, v) => {
      if (!acc[v.filter]) acc[v.filter] = [];
      acc[v.filter].push(v);
      return acc;
    },
    {},
  );

  return (
    <dl className="space-y-2">
      {Object.entries(grouped).map(([filterId, fvs]) => (
        <div key={filterId} className="flex gap-2 text-sm">
          <dt className="text-text-secondary w-28 shrink-0">
            Filter {filterId}
          </dt>
          <dd className="text-text-primary">
            {fvs.map((fv, i) => (
              <span key={fv.id}>
                {i > 0 && ", "}
                {fv.option !== null
                  ? `option:${fv.option}`
                  : fv.valueNumber !== null
                    ? fv.valueNumber
                    : fv.valueBoolean !== null
                      ? fv.valueBoolean
                        ? "Yes"
                        : "No"
                      : "—"}
              </span>
            ))}
          </dd>
        </div>
      ))}
    </dl>
  );
}
