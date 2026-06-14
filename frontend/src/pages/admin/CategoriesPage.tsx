import { useState } from "react";
import { CategoryTree } from "../../components/admin/CategoryTree";
import { FilterEditor } from "../../components/admin/FilterEditor";

export function CategoriesPage() {
  const [selectedCategory, setSelectedCategory] = useState<{
    id: number;
    slug: string;
  } | null>(null);

  return (
    <div>
      <h1 className="text-xl font-semibold text-text-primary mb-6">
        Categories
      </h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-border rounded-lg p-4">
          <CategoryTree
            selectedId={selectedCategory?.id}
            onSelectCategory={(id, slug) => setSelectedCategory({ id, slug })}
          />
        </div>
        <div className="bg-white border border-border rounded-lg p-4">
          {selectedCategory ? (
            <FilterEditor categoryId={selectedCategory.id} />
          ) : (
            <p className="text-text-secondary text-sm">
              Select a category to manage its filters.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
