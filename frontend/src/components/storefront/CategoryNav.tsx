import { useQuery } from "@tanstack/react-query";
import { NavLink } from "react-router";
import { type CategoryNode, storefront } from "../../lib/api";

export function CategoryNav() {
  const { data: tree, isLoading } = useQuery({
    queryKey: ["storefront", "categories"],
    queryFn: storefront.categories,
  });

  if (isLoading)
    return (
      <nav aria-label="Categories" className="text-text-secondary text-sm">
        Loading…
      </nav>
    );

  return (
    <nav aria-label="Category navigation">
      <h2 className="font-semibold text-text-primary mb-3 text-sm uppercase tracking-wide">
        Browse
      </h2>
      <ul className="space-y-0.5">
        {tree?.map((node) => (
          <CategoryNavNode key={node.id} node={node} depth={0} />
        ))}
      </ul>
    </nav>
  );
}

function CategoryNavNode({
  node,
  depth,
}: {
  node: CategoryNode;
  depth: number;
}) {
  return (
    <li>
      <NavLink
        to={`/category/${node.slug}`}
        className={({ isActive }) =>
          `block px-3 py-1.5 rounded text-sm transition-colors min-h-[44px] flex items-center ${
            isActive
              ? "bg-primary text-white"
              : "text-text-secondary hover:text-text-primary hover:bg-surface"
          }`
        }
        style={{ paddingLeft: `${depth * 12 + 12}px` }}
      >
        {node.name}
      </NavLink>
      {node.children.length > 0 && (
        <ul>
          {node.children.map((child) => (
            <CategoryNavNode key={child.id} node={child} depth={depth + 1} />
          ))}
        </ul>
      )}
    </li>
  );
}
