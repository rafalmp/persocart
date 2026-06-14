import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { ProductForm } from "../../components/admin/ProductForm";
import { Button } from "../../components/ui/Button";
import { useToast } from "../../components/ui/Toast";
import {
  type Category,
  categories,
  type Product,
  products,
} from "../../lib/api";

export function ProductsPage() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(
    null,
  );
  const [editingProduct, setEditingProduct] = useState<Product | null | "new">(
    null,
  );

  const { data: catList } = useQuery({
    queryKey: ["categories", "list"],
    queryFn: categories.list,
  });

  const { data: productList, isLoading } = useQuery({
    queryKey: ["products", selectedCategoryId],
    queryFn: () => products.list({ category: selectedCategoryId ?? undefined }),
    enabled: selectedCategoryId !== null,
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => products.remove(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["products"] });
      toast("Product deleted", "success");
    },
    onError: () => toast("Failed to delete product", "error"),
  });

  if (editingProduct !== null) {
    return (
      <div>
        <h1 className="text-xl font-semibold text-text-primary mb-6">
          {editingProduct === "new"
            ? "New Product"
            : `Edit: ${editingProduct.name}`}
        </h1>
        <div className="bg-white border border-border rounded-lg p-6 max-w-2xl">
          <ProductForm
            categoryId={selectedCategoryId!}
            product={editingProduct !== "new" ? editingProduct : undefined}
            onDone={() => setEditingProduct(null)}
          />
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-xl font-semibold text-text-primary mb-6">Products</h1>

      <div className="mb-4 flex flex-wrap gap-3 items-center">
        <label
          htmlFor="cat-filter"
          className="text-sm font-medium text-text-secondary"
        >
          Category:
        </label>
        <select
          id="cat-filter"
          value={selectedCategoryId ?? ""}
          onChange={(e) =>
            setSelectedCategoryId(
              e.target.value ? Number(e.target.value) : null,
            )
          }
          className="px-3 py-1.5 border border-border rounded text-sm min-h-[44px]"
        >
          <option value="">— select —</option>
          {catList?.results.map((c: Category) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        {selectedCategoryId && (
          <Button size="sm" onClick={() => setEditingProduct("new")}>
            + Add product
          </Button>
        )}
      </div>

      {selectedCategoryId === null && (
        <p className="text-text-secondary text-sm">
          Select a category to view its products.
        </p>
      )}

      {selectedCategoryId && isLoading && (
        <p className="text-text-secondary text-sm">Loading…</p>
      )}

      {productList && (
        <div className="bg-white border border-border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-surface border-b border-border">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">
                  Name
                </th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">
                  Price
                </th>
                <th className="px-4 py-3 text-left font-medium text-text-secondary">
                  Status
                </th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {productList.results.map((p: Product) => (
                <tr key={p.id} className="hover:bg-surface">
                  <td className="px-4 py-3 font-medium text-text-primary">
                    {p.name}
                  </td>
                  <td className="px-4 py-3 text-text-secondary">€{p.price}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${p.isActive ? "bg-green-100 text-success" : "bg-surface text-text-secondary"}`}
                    >
                      {p.isActive ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3 flex gap-2 justify-end">
                    <button
                      type="button"
                      onClick={() => setEditingProduct(p)}
                      className="text-primary text-xs hover:underline min-h-[44px] px-2"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        if (confirm(`Delete "${p.name}"?`))
                          deleteMut.mutate(p.id);
                      }}
                      className="text-error text-xs hover:underline min-h-[44px] px-2"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {productList.results.length === 0 && (
            <p className="px-4 py-6 text-text-secondary text-sm text-center">
              No products in this category.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
