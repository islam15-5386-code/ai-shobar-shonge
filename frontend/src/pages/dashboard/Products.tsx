import { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";
import { Plus, Search, Package, Trash2 } from "lucide-react";
import { toast } from "sonner";

type ProductItem = {
  id: number;
  name: string;
  description?: string;
  price: number;
  currency?: string;
  stock_status?: string;
  return_policy?: string;
  is_active?: boolean;
};

const stockBadge = (s: string) => {
  if (s === "in_stock") return <Badge variant="outline" className="bg-success/10 text-success border-success/20">In stock</Badge>;
  if (s === "low") return <Badge variant="outline" className="bg-warning/10 text-warning border-warning/20">Low stock</Badge>;
  return <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive/20">Out of stock</Badge>;
};

const emptyForm = {
  name: "",
  description: "",
  price: "",
  stock_status: "in_stock",
  return_policy: "7 days return",
};

export default function Products() {
  const [items, setItems] = useState<ProductItem[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [openAdd, setOpenAdd] = useState(false);
  const [form, setForm] = useState(emptyForm);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await apiFetch<any>("/api/products/");
      const rows = Array.isArray(data) ? data : data?.results || [];
      setItems(rows);
    } catch {
      toast.error("Product load failed. Please login first.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((p) => p.name.toLowerCase().includes(q) || String(p.description || "").toLowerCase().includes(q));
  }, [items, query]);

  const handleCreate = async () => {
    if (!form.name.trim() || !form.price.trim()) {
      toast.error("Name and price are required");
      return;
    }
    try {
      setSaving(true);
      await apiFetch("/api/products/", {
        method: "POST",
        body: JSON.stringify({
          name: form.name.trim(),
          description: form.description.trim(),
          price: Number(form.price),
          currency: "BDT",
          stock_status: (form.stock_status || "in_stock").trim().toLowerCase(),
          return_policy: form.return_policy.trim(),
          is_active: true,
        }),
      });
      toast.success("Product added");
      setOpenAdd(false);
      setForm(emptyForm);
      await loadProducts();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Add product failed";
      toast.error(message);
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = async (p: ProductItem) => {
    const name = window.prompt("Edit product name", p.name);
    if (!name) return;
    const price = window.prompt("Edit price (BDT)", String(p.price));
    if (!price) return;
    try {
      await apiFetch(`/api/products/${p.id}/`, {
        method: "PATCH",
        body: JSON.stringify({ name, price: Number(price) }),
      });
      toast.success("Product updated");
      await loadProducts();
    } catch {
      toast.error("Update failed");
    }
  };

  const handleDelete = async (p: ProductItem) => {
    if (!window.confirm(`Delete product: ${p.name}?`)) return;
    try {
      await apiFetch(`/api/products/${p.id}/`, { method: "DELETE" });
      toast.success("Product deleted");
      await loadProducts();
    } catch {
      toast.error("Delete failed");
    }
  };

  const inStock = items.filter((p) => p.stock_status === "in_stock").length;
  const outStock = items.filter((p) => p.stock_status === "out" || p.stock_status === "out_of_stock").length;

  return (
    <div className="p-4 md:p-8">
      <PageHeader
        title="Products & Services"
        subtitle="Manage your catalog so AI can answer accurately"
        actions={
          <Dialog open={openAdd} onOpenChange={setOpenAdd}>
            <DialogTrigger asChild>
              <Button className="gradient-primary border-0"><Plus className="w-4 h-4 mr-1" /> Add Product</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Add Product</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <div className="space-y-2"><Label>Name</Label><Input value={form.name} onChange={(e) => setForm((s) => ({ ...s, name: e.target.value }))} /></div>
                <div className="space-y-2"><Label>Description</Label><Textarea rows={3} value={form.description} onChange={(e) => setForm((s) => ({ ...s, description: e.target.value }))} /></div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2"><Label>Price (BDT)</Label><Input type="number" value={form.price} onChange={(e) => setForm((s) => ({ ...s, price: e.target.value }))} /></div>
                  <div className="space-y-2"><Label>Stock Status</Label><Input value={form.stock_status} onChange={(e) => setForm((s) => ({ ...s, stock_status: e.target.value }))} /></div>
                </div>
                <div className="space-y-2"><Label>Return Policy</Label><Input value={form.return_policy} onChange={(e) => setForm((s) => ({ ...s, return_policy: e.target.value }))} /></div>
                <Button className="w-full gradient-primary border-0" onClick={handleCreate} disabled={saving}>{saving ? "Saving..." : "Save Product"}</Button>
              </div>
            </DialogContent>
          </Dialog>
        }
      />

      <div className="grid sm:grid-cols-3 gap-4 mb-6">
        <Card className="p-5"><div className="text-xs text-muted-foreground">Total Products</div><div className="text-2xl font-bold mt-1">{loading ? "..." : items.length}</div></Card>
        <Card className="p-5"><div className="text-xs text-muted-foreground">In Stock</div><div className="text-2xl font-bold mt-1 text-success">{loading ? "..." : inStock}</div></Card>
        <Card className="p-5"><div className="text-xs text-muted-foreground">Out of Stock</div><div className="text-2xl font-bold mt-1 text-destructive">{loading ? "..." : outStock}</div></Card>
      </div>

      <Card>
        <div className="p-4 border-b">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input placeholder="Search products..." className="pl-9 bg-muted/50 border-0" value={query} onChange={(e) => setQuery(e.target.value)} />
          </div>
        </div>
        <Table>
          <TableHeader><TableRow>
            <TableHead>Product</TableHead>
            <TableHead>Price</TableHead>
            <TableHead className="hidden md:table-cell">Stock</TableHead>
            <TableHead className="hidden lg:table-cell">Policy</TableHead>
            <TableHead className="text-right">Action</TableHead>
          </TableRow></TableHeader>
          <TableBody>
            {filtered.map((p) => (
              <TableRow key={p.id} className="hover:bg-muted/30">
                <TableCell>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center"><Package className="w-5 h-5 text-muted-foreground" /></div>
                    <div>
                      <div className="font-medium">{p.name}</div>
                      <div className="text-xs text-muted-foreground">{p.description || "No description"}</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="font-semibold">৳{Number(p.price || 0).toLocaleString()}</TableCell>
                <TableCell className="hidden md:table-cell">{stockBadge(p.stock_status || "out")}</TableCell>
                <TableCell className="hidden lg:table-cell text-sm text-muted-foreground">{p.return_policy || "-"}</TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="sm" onClick={() => handleEdit(p)}>Edit</Button>
                  <Button variant="ghost" size="icon" className="w-8 h-8 text-destructive" onClick={() => handleDelete(p)}><Trash2 className="w-3.5 h-3.5" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
