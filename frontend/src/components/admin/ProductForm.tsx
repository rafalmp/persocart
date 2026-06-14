import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import {
  type CategoryFilter,
  categories,
  type Product,
  products,
} from "../../lib/api";
import { Button } from "../ui/Button";
import { useToast } from "../ui/Toast";

interface Props {
  categoryId: number;
  product?: Product;
  onDone: () => void;
}

interface FilterValueState {
  filterId: number;
  optionId?: number;
  valueNumber?: string;
  valueBoolean?: boolean;
  // For multichoice: multiple optionIds
  optionIds?: number[];
}

export function ProductForm({ categoryId, product, onDone }: Props) {
  const qc = useQueryClient();
  const { toast } = useToast();
  const isEdit = !!product;

  const [name, setName] = useState(product?.name ?? "");
  const [description, setDescription] = useState(product?.description ?? "");
  const [price, setPrice] = useState(product?.price ?? "");
  const [isActive, setIsActive] = useState(product?.isActive ?? true);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [altText, setAltText] = useState(product?.alt_text ?? "");
  const [filterValues, setFilterValues] = useState<
    Record<number, FilterValueState>
  >({});
  const [validationError, setValidationError] = useState("");

  const { data: catFilters } = useQuery({
    queryKey: ["categories", categoryId, "filters"],
    queryFn: () => categories.filters(categoryId),
  });

  // Initialize filter values from existing product
  useEffect(() => {
    if (product?.filterValues && catFilters) {
      const init: Record<number, FilterValueState> = {};
      for (const fv of product.filterValues) {
        const f = catFilters.find((f: CategoryFilter) => f.id === fv.filter);
        if (!f) continue;
        if (f.type === "multichoice") {
          if (!init[fv.filter]) {
            init[fv.filter] = { filterId: fv.filter, optionIds: [] };
          }
          if (fv.option)
            init[fv.filter].optionIds = [
              ...(init[fv.filter].optionIds ?? []),
              fv.option,
            ];
        } else {
          init[fv.filter] = {
            filterId: fv.filter,
            optionId: fv.option ?? undefined,
            valueNumber: fv.valueNumber ?? undefined,
            valueBoolean: fv.valueBoolean ?? undefined,
          };
        }
      }
      setFilterValues(init);
    }
  }, [product, catFilters]);

  const saveMut = useMutation({
    mutationFn: async () => {
      const fd = new FormData();
      fd.append("category", String(categoryId));
      fd.append("name", name);
      fd.append("description", description);
      fd.append("price", price);
      fd.append("isActive", String(isActive));
      fd.append("alt_text", altText);
      if (imageFile) fd.append("image", imageFile);

      const saved = isEdit
        ? await products.update(product.id, fd)
        : await products.create(fd);

      // Set filter values
      const values: {
        filter: number;
        option?: number;
        valueNumber?: string;
        valueBoolean?: boolean;
      }[] = [];
      for (const fv of Object.values(filterValues)) {
        const f = catFilters?.find(
          (cf: CategoryFilter) => cf.id === fv.filterId,
        );
        if (!f) continue;
        if (f.type === "multichoice") {
          for (const optId of fv.optionIds ?? []) {
            values.push({ filter: fv.filterId, option: optId });
          }
        } else if (f.type === "choice" && fv.optionId) {
          values.push({ filter: fv.filterId, option: fv.optionId });
        } else if (f.type === "number" && fv.valueNumber) {
          values.push({ filter: fv.filterId, valueNumber: fv.valueNumber });
        } else if (f.type === "boolean" && fv.valueBoolean !== undefined) {
          values.push({ filter: fv.filterId, valueBoolean: fv.valueBoolean });
        }
      }

      if (values.length > 0) {
        await products.setFilterValues(saved.id, values);
      }
      return saved;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["products"] });
      toast(isEdit ? "Product updated" : "Product created", "success");
      onDone();
    },
    onError: (err: Error) => {
      setValidationError(err.message || "Failed to save product");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError("");
    if (Number(price) < 0) {
      setValidationError("Price must be 0 or greater.");
      return;
    }
    saveMut.mutate();
  };

  return (
    <form
      onSubmit={handleSubmit}
      aria-label={isEdit ? "Edit product" : "Create product"}
      className="space-y-4"
    >
      {validationError && (
        <div
          role="alert"
          className="p-3 bg-red-50 border border-error rounded text-error text-sm"
        >
          {validationError}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <label
            htmlFor="pf-name"
            className="block text-sm font-medium text-text-primary mb-1"
          >
            Name *
          </label>
          <input
            id="pf-name"
            required
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-border rounded text-sm min-h-[44px]"
          />
        </div>
        <div>
          <label
            htmlFor="pf-price"
            className="block text-sm font-medium text-text-primary mb-1"
          >
            Price (€) *
          </label>
          <input
            id="pf-price"
            required
            type="number"
            min="0"
            step="0.01"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            className="w-full px-3 py-2 border border-border rounded text-sm min-h-[44px]"
          />
        </div>
        <div className="flex items-center gap-3 pt-6">
          <input
            id="is-active"
            type="checkbox"
            checked={isActive}
            onChange={(e) => setIsActive(e.target.checked)}
            className="w-4 h-4"
          />
          <label htmlFor="is-active" className="text-sm text-text-primary">
            Active (visible on storefront)
          </label>
        </div>
      </div>

      <div>
        <label
          htmlFor="pf-description"
          className="block text-sm font-medium text-text-primary mb-1"
        >
          Description
        </label>
        <textarea
          id="pf-description"
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded text-sm"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="pf-image"
            className="block text-sm font-medium text-text-primary mb-1"
          >
            Image
          </label>
          {product?.imageUrl && !imageFile && (
            <img
              src={product.imageUrl}
              alt={product.alt_text || product.name}
              className="w-20 h-20 object-cover rounded mb-2"
            />
          )}
          <input
            id="pf-image"
            type="file"
            accept="image/*"
            onChange={(e) => setImageFile(e.target.files?.[0] ?? null)}
            className="text-sm text-text-secondary"
          />
        </div>
        <div>
          <label
            htmlFor="pf-alt-text"
            className="block text-sm font-medium text-text-primary mb-1"
          >
            Image alt text {imageFile || product?.imageUrl ? "*" : ""}
          </label>
          <input
            id="pf-alt-text"
            type="text"
            value={altText}
            onChange={(e) => setAltText(e.target.value)}
            className="w-full px-3 py-2 border border-border rounded text-sm min-h-[44px]"
            placeholder="Describe the image for screen readers"
          />
        </div>
      </div>

      {catFilters && catFilters.length > 0 && (
        <fieldset className="border border-border rounded-md p-4">
          <legend className="text-sm font-medium text-text-primary px-2">
            Filter values
          </legend>
          <div className="space-y-3">
            {catFilters.map((f: CategoryFilter) => (
              <FilterValueInput
                key={f.id}
                filter={f}
                value={filterValues[f.id]}
                onChange={(v) =>
                  setFilterValues({ ...filterValues, [f.id]: v })
                }
              />
            ))}
          </div>
        </fieldset>
      )}

      <div className="flex gap-3">
        <Button type="submit" disabled={saveMut.isPending}>
          {saveMut.isPending ? "Saving…" : isEdit ? "Update" : "Create"}
        </Button>
        <Button variant="secondary" onClick={onDone}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

function FilterValueInput({
  filter,
  value,
  onChange,
}: {
  filter: CategoryFilter;
  value?: FilterValueState;
  onChange: (v: FilterValueState) => void;
}) {
  const base = { filterId: filter.id };

  switch (filter.type) {
    case "choice":
      return (
        <div>
          <label
            htmlFor={`fv-choice-${filter.id}`}
            className="block text-xs font-medium text-text-secondary mb-1"
          >
            {filter.name}
          </label>
          <select
            id={`fv-choice-${filter.id}`}
            value={value?.optionId ?? ""}
            onChange={(e) =>
              onChange({
                ...base,
                optionId: Number(e.target.value) || undefined,
              })
            }
            className="w-full px-2 py-1.5 border border-border rounded text-sm min-h-[44px]"
          >
            <option value="">— select —</option>
            {filter.options.map((o) => (
              <option key={o.id} value={o.id}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
      );

    case "multichoice":
      return (
        <fieldset>
          <legend className="text-xs font-medium text-text-secondary mb-1">
            {filter.name}
          </legend>
          <div className="flex flex-wrap gap-2">
            {filter.options.map((o) => {
              const selected = value?.optionIds?.includes(o.id) ?? false;
              return (
                <label key={o.id} className="flex items-center gap-1.5 text-sm">
                  <input
                    type="checkbox"
                    checked={selected}
                    onChange={(e) => {
                      const ids = value?.optionIds ?? [];
                      onChange({
                        ...base,
                        optionIds: e.target.checked
                          ? [...ids, o.id]
                          : ids.filter((i) => i !== o.id),
                      });
                    }}
                    className="w-4 h-4"
                  />
                  {o.label}
                </label>
              );
            })}
          </div>
        </fieldset>
      );

    case "number":
      return (
        <div>
          <label
            htmlFor={`fv-number-${filter.id}`}
            className="block text-xs font-medium text-text-secondary mb-1"
          >
            {filter.name}
            {filter.unit ? ` (${filter.unit})` : ""}
          </label>
          <input
            id={`fv-number-${filter.id}`}
            type="number"
            step="any"
            value={value?.valueNumber ?? ""}
            onChange={(e) => onChange({ ...base, valueNumber: e.target.value })}
            className="w-full px-2 py-1.5 border border-border rounded text-sm min-h-[44px]"
          />
        </div>
      );

    case "boolean":
      return (
        <div className="flex items-center gap-2">
          <input
            id={`bf-${filter.id}`}
            type="checkbox"
            checked={value?.valueBoolean ?? false}
            onChange={(e) =>
              onChange({ ...base, valueBoolean: e.target.checked })
            }
            className="w-4 h-4"
          />
          <label
            htmlFor={`bf-${filter.id}`}
            className="text-sm text-text-primary"
          >
            {filter.name}
          </label>
        </div>
      );
  }
}
