import { useQuery } from "@tanstack/react-query";
import { type CategoryFilter, storefront } from "../../lib/api";

interface Props {
  categorySlug: string;
  activeFilters: Record<string, string | string[]>;
  onChange: (filters: Record<string, string | string[]>) => void;
}

export function FilterPanel({ categorySlug, activeFilters, onChange }: Props) {
  const { data: catFilters, isLoading } = useQuery({
    queryKey: ["storefront", "filters", categorySlug],
    queryFn: () => storefront.categoryFilters(categorySlug),
  });

  if (isLoading)
    return <div className="text-text-secondary text-sm">Loading filters…</div>;
  if (!catFilters?.length) return null;

  const hasActiveFilters = Object.values(activeFilters).some((v) =>
    Array.isArray(v) ? v.length > 0 : v !== "",
  );

  return (
    <aside aria-label="Product filters">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold text-sm text-text-primary uppercase tracking-wide">
          Filters
        </h2>
        {hasActiveFilters && (
          <button
            type="button"
            onClick={() => onChange({})}
            className="text-xs text-primary hover:underline min-h-[44px] px-1"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Active filter chips */}
      {hasActiveFilters && (
        <section
          aria-label="Active filters"
          className="flex flex-wrap gap-1 mb-3"
        >
          {Object.entries(activeFilters).map(([key, val]) => {
            const vals = Array.isArray(val) ? val : [val];
            return vals.map((v) => (
              <span
                key={`${key}-${v}`}
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-primary/10 text-primary rounded-full text-xs"
              >
                {v}
                <button
                  type="button"
                  onClick={() => {
                    const next = { ...activeFilters };
                    if (Array.isArray(activeFilters[key])) {
                      const remaining = (activeFilters[key] as string[]).filter(
                        (x) => x !== v,
                      );
                      if (remaining.length) next[key] = remaining;
                      else delete next[key];
                    } else {
                      delete next[key];
                    }
                    onChange(next);
                  }}
                  aria-label={`Remove filter ${v}`}
                  className="hover:text-primary-dark"
                >
                  ✕
                </button>
              </span>
            ));
          })}
        </section>
      )}

      <div className="space-y-4">
        {catFilters.map((f: CategoryFilter) => (
          <FilterWidget
            key={f.id}
            filter={f}
            value={activeFilters[f.slug]}
            onChange={(val) => {
              const next = { ...activeFilters };
              if (
                val === undefined ||
                (Array.isArray(val) && val.length === 0) ||
                val === ""
              ) {
                delete next[f.slug];
              } else {
                next[f.slug] = val;
              }
              onChange(next);
            }}
          />
        ))}
      </div>
    </aside>
  );
}

function FilterWidget({
  filter,
  value,
  onChange,
}: {
  filter: CategoryFilter;
  value: string | string[] | undefined;
  onChange: (v: string | string[] | undefined) => void;
}) {
  return (
    <fieldset>
      <legend className="text-sm font-medium text-text-primary mb-2">
        {filter.name}
      </legend>

      {filter.type === "choice" && (
        <div className="space-y-1">
          {filter.options.map((opt) => (
            <label
              key={opt.id}
              className="flex items-center gap-2 text-sm min-h-[44px]"
            >
              <input
                type="radio"
                name={`filter-${filter.id}`}
                value={opt.value}
                checked={value === opt.value}
                onChange={() => onChange(opt.value)}
                className="w-4 h-4"
              />
              {opt.label}
            </label>
          ))}
          {value && (
            <button
              type="button"
              onClick={() => onChange(undefined)}
              className="text-xs text-text-secondary hover:text-primary mt-1 min-h-[36px]"
            >
              Clear
            </button>
          )}
        </div>
      )}

      {filter.type === "multichoice" && (
        <div className="space-y-1">
          {filter.options.map((opt) => {
            const selected = Array.isArray(value)
              ? value.includes(opt.value)
              : false;
            return (
              <label
                key={opt.id}
                className="flex items-center gap-2 text-sm min-h-[44px]"
              >
                <input
                  type="checkbox"
                  value={opt.value}
                  checked={selected}
                  onChange={(e) => {
                    const current = Array.isArray(value) ? value : [];
                    onChange(
                      e.target.checked
                        ? [...current, opt.value]
                        : current.filter((v) => v !== opt.value),
                    );
                  }}
                  className="w-4 h-4"
                />
                {opt.label}
              </label>
            );
          })}
        </div>
      )}

      {filter.type === "number" && (
        <div className="flex gap-2 items-center text-sm">
          <input
            type="number"
            step="any"
            placeholder="Min"
            value={
              typeof value === "string" && value.startsWith("min:")
                ? value.slice(4)
                : ""
            }
            onChange={(e) =>
              onChange(e.target.value ? `min:${e.target.value}` : undefined)
            }
            className="w-24 px-2 py-1.5 border border-border rounded text-sm min-h-[44px]"
            aria-label={`${filter.name} minimum`}
          />
          <span className="text-text-secondary">–</span>
          <input
            type="number"
            step="any"
            placeholder="Max"
            value={
              typeof value === "string" && value.startsWith("max:")
                ? value.slice(4)
                : ""
            }
            onChange={(e) =>
              onChange(e.target.value ? `max:${e.target.value}` : undefined)
            }
            className="w-24 px-2 py-1.5 border border-border rounded text-sm min-h-[44px]"
            aria-label={`${filter.name} maximum`}
          />
          {filter.unit && (
            <span className="text-text-secondary">{filter.unit}</span>
          )}
        </div>
      )}

      {filter.type === "boolean" && (
        <label className="flex items-center gap-2 text-sm min-h-[44px]">
          <input
            type="checkbox"
            checked={value === "true"}
            onChange={(e) => onChange(e.target.checked ? "true" : undefined)}
            className="w-4 h-4"
          />
          {filter.name}
        </label>
      )}
    </fieldset>
  );
}
