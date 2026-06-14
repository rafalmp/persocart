import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  type CategoryFilter,
  categories,
  type FilterType,
  filters,
} from "../../lib/api";
import { Button } from "../ui/Button";
import { useToast } from "../ui/Toast";

interface Props {
  categoryId: number;
}

const FILTER_TYPES: { value: FilterType; label: string }[] = [
  { value: "choice", label: "Single choice" },
  { value: "multichoice", label: "Multiple choice" },
  { value: "number", label: "Number" },
  { value: "boolean", label: "Boolean" },
];

export function FilterEditor({ categoryId }: Props) {
  const qc = useQueryClient();
  const { toast } = useToast();

  const { data: catFilters, isLoading } = useQuery({
    queryKey: ["categories", categoryId, "filters"],
    queryFn: () => categories.filters(categoryId),
  });

  const [adding, setAdding] = useState(false);
  const [form, setForm] = useState<{
    name: string;
    type: FilterType;
    unit: string;
    options: { label: string; value: string }[];
  }>({ name: "", type: "choice", unit: "", options: [] });

  const createMut = useMutation({
    mutationFn: () =>
      filters.createForCategory(categoryId, {
        name: form.name,
        type: form.type,
        unit: form.unit || undefined,
        options: needsOptions(form.type) ? form.options : undefined,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categories", categoryId, "filters"] });
      setAdding(false);
      setForm({ name: "", type: "choice", unit: "", options: [] });
      toast("Filter created", "success");
    },
    onError: () => toast("Failed to create filter", "error"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => filters.remove(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categories", categoryId, "filters"] });
      toast("Filter deleted", "success");
    },
    onError: () => toast("Failed to delete filter", "error"),
  });

  const needsOptions = (t: FilterType) => t === "choice" || t === "multichoice";

  if (isLoading)
    return <p className="text-text-secondary text-sm">Loading filters…</p>;

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-text-primary">Filters</h3>
        <Button size="sm" onClick={() => setAdding(true)}>
          + Add filter
        </Button>
      </div>

      {adding && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            createMut.mutate();
          }}
          className="mb-4 p-4 border border-border rounded-md space-y-3"
          aria-label="New filter form"
        >
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label
                htmlFor="fe-name"
                className="block text-xs font-medium text-text-secondary mb-1"
              >
                Name
              </label>
              <input
                id="fe-name"
                required
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full px-2 py-1.5 border border-border rounded text-sm min-h-[44px]"
              />
            </div>
            <div>
              <label
                htmlFor="fe-type"
                className="block text-xs font-medium text-text-secondary mb-1"
              >
                Type
              </label>
              <select
                id="fe-type"
                value={form.type}
                onChange={(e) =>
                  setForm({
                    ...form,
                    type: e.target.value as FilterType,
                    options: [],
                  })
                }
                className="w-full px-2 py-1.5 border border-border rounded text-sm min-h-[44px]"
              >
                {FILTER_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {form.type === "number" && (
            <div>
              <label
                htmlFor="fe-unit"
                className="block text-xs font-medium text-text-secondary mb-1"
              >
                Unit (optional)
              </label>
              <input
                id="fe-unit"
                type="text"
                placeholder="e.g. g, kg, cm"
                value={form.unit}
                onChange={(e) => setForm({ ...form, unit: e.target.value })}
                className="w-full px-2 py-1.5 border border-border rounded text-sm min-h-[44px]"
              />
            </div>
          )}

          {needsOptions(form.type) && (
            <div>
              <p className="text-xs font-medium text-text-secondary mb-1">
                Options
              </p>
              {form.options.map((opt, i) => (
                // biome-ignore lint/suspicious/noArrayIndexKey: options have no stable ID before save
                <div key={i} className="flex gap-2 mb-1">
                  <input
                    type="text"
                    placeholder="Label"
                    value={opt.label}
                    onChange={(e) => {
                      const opts = [...form.options];
                      opts[i] = { ...opts[i], label: e.target.value };
                      setForm({ ...form, options: opts });
                    }}
                    className="flex-1 px-2 py-1 border border-border rounded text-sm"
                  />
                  <input
                    type="text"
                    placeholder="Value"
                    value={opt.value}
                    onChange={(e) => {
                      const opts = [...form.options];
                      opts[i] = { ...opts[i], value: e.target.value };
                      setForm({ ...form, options: opts });
                    }}
                    className="flex-1 px-2 py-1 border border-border rounded text-sm"
                  />
                  <button
                    type="button"
                    onClick={() =>
                      setForm({
                        ...form,
                        options: form.options.filter((_, j) => j !== i),
                      })
                    }
                    className="text-error text-sm px-1 min-h-[44px]"
                    aria-label="Remove option"
                  >
                    ✕
                  </button>
                </div>
              ))}
              <Button
                type="button"
                size="sm"
                variant="secondary"
                onClick={() =>
                  setForm({
                    ...form,
                    options: [...form.options, { label: "", value: "" }],
                  })
                }
              >
                + Option
              </Button>
            </div>
          )}

          <div className="flex gap-2">
            <Button type="submit" size="sm" disabled={createMut.isPending}>
              Save
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setAdding(false)}>
              Cancel
            </Button>
          </div>
        </form>
      )}

      <ul className="space-y-2">
        {catFilters?.map((f: CategoryFilter) => (
          <li
            key={f.id}
            className="flex items-start gap-3 p-3 border border-border rounded-md"
          >
            <div className="flex-1 min-w-0">
              <div className="font-medium text-sm text-text-primary">
                {f.name}
              </div>
              <div className="text-xs text-text-secondary">
                {f.type}
                {f.unit ? ` (${f.unit})` : ""}
                {f.options.length > 0 && ` · ${f.options.length} options`}
              </div>
            </div>
            <button
              type="button"
              onClick={() => {
                if (
                  confirm(
                    `Delete filter "${f.name}"? This removes all assigned product values.`,
                  )
                ) {
                  deleteMut.mutate(f.id);
                }
              }}
              className="text-xs text-text-secondary hover:text-error min-h-[44px] px-2"
              aria-label={`Delete filter ${f.name}`}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>

      {catFilters?.length === 0 && !adding && (
        <p className="text-text-secondary text-sm italic">
          No filters defined for this category.
        </p>
      )}
    </div>
  );
}
