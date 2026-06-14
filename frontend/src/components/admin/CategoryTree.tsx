import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { type CategoryNode, categories } from "../../lib/api";
import { Button } from "../ui/Button";
import { useToast } from "../ui/Toast";

interface Props {
  onSelectCategory?: (id: number, slug: string) => void;
  selectedId?: number;
}

export function CategoryTree({ onSelectCategory, selectedId }: Props) {
  const qc = useQueryClient();
  const { toast } = useToast();
  const { data: tree, isLoading } = useQuery({
    queryKey: ["categories", "tree"],
    queryFn: categories.tree,
  });

  const [creating, setCreating] = useState<{ parentId: number | null } | null>(
    null,
  );
  const [newName, setNewName] = useState("");
  const [deleting, setDeleting] = useState<CategoryNode | null>(null);

  const createMut = useMutation({
    mutationFn: (name: string) =>
      categories.create({ name, parent: creating?.parentId ?? null }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categories"] });
      setCreating(null);
      setNewName("");
      toast("Category created", "success");
    },
    onError: () => toast("Failed to create category", "error"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => categories.remove(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categories"] });
      setDeleting(null);
      toast("Category deleted", "success");
    },
    onError: () => toast("Failed to delete category", "error"),
  });

  if (isLoading) return <p className="text-text-secondary text-sm">Loading…</p>;

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold text-text-primary">Categories</h2>
        <Button
          size="sm"
          onClick={() => {
            setCreating({ parentId: null });
            setNewName("");
          }}
        >
          + Add root
        </Button>
      </div>

      {creating?.parentId === null && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            createMut.mutate(newName);
          }}
          className="mb-3 flex gap-2"
        >
          <input
            // biome-ignore lint/a11y/noAutofocus: intentional focus for inline form
            autoFocus
            type="text"
            placeholder="Category name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="flex-1 px-2 py-1 border border-border rounded text-sm min-h-[44px]"
            aria-label="New root category name"
          />
          <Button size="sm" type="submit" disabled={!newName.trim()}>
            Save
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setCreating(null)}>
            Cancel
          </Button>
        </form>
      )}

      {/* biome-ignore lint/a11y/noNoninteractiveElementToInteractiveRole: ul with role="tree" is the standard ARIA tree pattern */}
      <ul className="space-y-0.5" role="tree" aria-label="Category tree">
        {tree?.map((node) => (
          <CategoryNodeRow
            key={node.id}
            node={node}
            depth={0}
            selectedId={selectedId}
            creating={creating}
            newName={newName}
            setNewName={setNewName}
            setCreating={setCreating}
            onSelect={onSelectCategory}
            onDelete={setDeleting}
            createMut={createMut}
          />
        ))}
      </ul>

      {tree?.length === 0 && (
        <p className="text-text-secondary text-sm italic">No categories yet.</p>
      )}

      {/* Delete confirmation dialog */}
      {deleting && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="del-title"
          className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
        >
          <div className="bg-white rounded-lg p-6 max-w-sm w-full shadow-lg">
            <h3 id="del-title" className="font-semibold text-text-primary mb-2">
              Delete &ldquo;{deleting.name}&rdquo;?
            </h3>
            <p className="text-text-secondary text-sm mb-4">
              This will permanently delete the category, all its subcategories,
              and associated products. This action cannot be undone.
            </p>
            <div className="flex gap-2 justify-end">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setDeleting(null)}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                size="sm"
                disabled={deleteMut.isPending}
                onClick={() => deleteMut.mutate(deleting.id)}
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function CategoryNodeRow({
  node,
  depth,
  selectedId,
  creating,
  newName,
  setNewName,
  setCreating,
  onSelect,
  onDelete,
  createMut,
}: {
  node: CategoryNode;
  depth: number;
  selectedId?: number;
  creating: { parentId: number | null } | null;
  newName: string;
  setNewName: (v: string) => void;
  setCreating: (v: { parentId: number | null } | null) => void;
  onSelect?: (id: number, slug: string) => void;
  onDelete: (node: CategoryNode) => void;
  createMut: ReturnType<typeof useMutation<unknown, Error, string>>;
}) {
  const [expanded, setExpanded] = useState(true);
  const hasChildren = node.children.length > 0;
  const isSelected = selectedId === node.id;

  return (
    <li
      role="treeitem"
      tabIndex={-1}
      aria-expanded={hasChildren ? expanded : undefined}
    >
      <div
        className={`flex items-center gap-1 px-2 py-1 rounded text-sm group ${isSelected ? "bg-primary/10 text-primary" : "hover:bg-surface"}`}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
      >
        {hasChildren ? (
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="w-5 h-5 flex items-center justify-center text-text-secondary"
            aria-label={expanded ? "Collapse" : "Expand"}
          >
            {expanded ? "▾" : "▸"}
          </button>
        ) : (
          <span className="w-5" />
        )}
        <button
          type="button"
          onClick={() => onSelect?.(node.id, node.slug)}
          className="flex-1 text-left truncate min-h-[36px] flex items-center"
        >
          {node.name}
        </button>
        <div className="opacity-0 group-hover:opacity-100 flex gap-1">
          <button
            type="button"
            onClick={() => {
              setCreating({ parentId: node.id });
              setNewName("");
            }}
            className="text-xs text-text-secondary hover:text-primary px-1 min-h-[36px]"
            aria-label={`Add child to ${node.name}`}
          >
            +
          </button>
          <button
            type="button"
            onClick={() => onDelete(node)}
            className="text-xs text-text-secondary hover:text-error px-1 min-h-[36px]"
            aria-label={`Delete ${node.name}`}
          >
            ✕
          </button>
        </div>
      </div>

      {creating?.parentId === node.id && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            createMut.mutate(newName);
          }}
          className="flex gap-2 mt-1"
          style={{ paddingLeft: `${(depth + 1) * 16 + 8}px` }}
        >
          <input
            // biome-ignore lint/a11y/noAutofocus: intentional focus for inline form
            autoFocus
            type="text"
            placeholder="Child name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="flex-1 px-2 py-1 border border-border rounded text-sm min-h-[44px]"
            aria-label="New child category name"
          />
          <Button size="sm" type="submit" disabled={!newName.trim()}>
            Save
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setCreating(null)}>
            ✕
          </Button>
        </form>
      )}

      {expanded && hasChildren && (
        <>
          {/* biome-ignore lint/a11y/useSemanticElements: ul with role="group" is standard ARIA tree child group */}
          <ul role="group">
            {node.children.map((child) => (
              <CategoryNodeRow
                key={child.id}
                node={child}
                depth={depth + 1}
                selectedId={selectedId}
                creating={creating}
                newName={newName}
                setNewName={setNewName}
                setCreating={setCreating}
                onSelect={onSelect}
                onDelete={onDelete}
                createMut={createMut}
              />
            ))}
          </ul>
        </>
      )}
    </li>
  );
}
