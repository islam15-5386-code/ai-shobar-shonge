import { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

type Category = {
  id: number;
  name: string;
  slug: string;
  parent: number | null;
  is_active: boolean;
};

const toSlug = (v: string) => v.toLowerCase().trim().replace(/[^a-z0-9\s-]/g, "").replace(/\s+/g, "-").replace(/-+/g, "-");

export default function CategoriesPage() {
  const [rows, setRows] = useState<Category[]>([]);
  const [name, setName] = useState("");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    try {
      setLoading(true);
      const data = await apiFetch<Category[]>("/api/marketplace/categories/");
      setRows(data || []);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to load categories";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((c) => c.name.toLowerCase().includes(q) || c.slug.toLowerCase().includes(q));
  }, [rows, query]);

  const add = async () => {
    if (!name.trim()) {
      toast.error("Category name required");
      return;
    }
    try {
      setSaving(true);
      await apiFetch("/api/marketplace/categories/", {
        method: "POST",
        body: JSON.stringify({ name: name.trim(), slug: toSlug(name) }),
      });
      setName("");
      toast.success("Category added");
      await load();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Add category failed";
      toast.error(message);
    } finally {
      setSaving(false);
    }
  };

  const editCategory = async (c: Category) => {
    const nextName = window.prompt("Edit category name", c.name);
    if (!nextName || !nextName.trim()) return;
    try {
      await apiFetch(`/api/marketplace/categories/${c.id}/`, {
        method: "PATCH",
        body: JSON.stringify({ name: nextName.trim(), slug: toSlug(nextName) }),
      });
      toast.success("Category updated");
      await load();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Update failed";
      toast.error(message);
    }
  };

  const toggleActive = async (c: Category) => {
    try {
      await apiFetch(`/api/marketplace/categories/${c.id}/`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !c.is_active }),
      });
      toast.success(c.is_active ? "Category deactivated" : "Category activated");
      await load();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Status update failed";
      toast.error(message);
    }
  };

  const removeCategory = async (c: Category) => {
    if (!window.confirm(`Delete category: ${c.name}?`)) return;
    try {
      await apiFetch(`/api/marketplace/categories/${c.id}/`, { method: "DELETE" });
      toast.success("Category deleted");
      await load();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Delete failed";
      toast.error(message);
    }
  };

  return (
    <div className="p-4 md:p-8 space-y-4">
      <PageHeader
        title="Categories"
        subtitle="Marketplace category management"
        actions={<Button variant="outline" onClick={load} disabled={loading}>{loading ? "Loading..." : "Refresh"}</Button>}
      />

      <Card className="p-4 flex gap-2">
        <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Category name" />
        <Button onClick={add} disabled={saving}>{saving ? "Adding..." : "Add"}</Button>
      </Card>

      <Card className="p-4">
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search category" className="max-w-sm" />
      </Card>

      <Card className="p-4 space-y-2">
        {filtered.map((c) => (
          <div key={c.id} className="border rounded p-3 flex flex-wrap items-center justify-between gap-2">
            <div>
              <div className="font-medium">{c.name}</div>
              <div className="text-xs text-muted-foreground">slug: {c.slug || "-"}</div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className={c.is_active ? "bg-success/10 text-success border-success/20" : ""}>
                {c.is_active ? "active" : "inactive"}
              </Badge>
              <Button size="sm" variant="outline" onClick={() => editCategory(c)}>Edit</Button>
              <Button size="sm" variant="outline" onClick={() => toggleActive(c)}>{c.is_active ? "Deactivate" : "Activate"}</Button>
              <Button size="sm" variant="outline" onClick={() => removeCategory(c)}>Delete</Button>
            </div>
          </div>
        ))}
        {!loading && filtered.length === 0 && <div className="text-sm text-muted-foreground py-8 text-center">No categories found.</div>}
      </Card>
    </div>
  );
}
