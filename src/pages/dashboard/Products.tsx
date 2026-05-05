import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { products } from "@/lib/mockData";
import { Plus, Search, Package } from "lucide-react";

const stockBadge = (s: string) => {
  if (s === "in_stock") return <Badge variant="outline" className="bg-success/10 text-success border-success/20">In stock</Badge>;
  if (s === "low") return <Badge variant="outline" className="bg-warning/10 text-warning border-warning/20">Low stock</Badge>;
  return <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive/20">Out of stock</Badge>;
};

export default function Products() {
  return (
    <div className="p-4 md:p-8">
      <PageHeader title="Products & Services" subtitle="Manage your catalog so AI can answer accurately" actions={<Button className="gradient-primary border-0"><Plus className="w-4 h-4 mr-1" /> Add Product</Button>} />

      <div className="grid sm:grid-cols-3 gap-4 mb-6">
        <Card className="p-5"><div className="text-xs text-muted-foreground">Total Products</div><div className="text-2xl font-bold mt-1">{products.length}</div></Card>
        <Card className="p-5"><div className="text-xs text-muted-foreground">In Stock</div><div className="text-2xl font-bold mt-1 text-success">{products.filter(p => p.stock === "in_stock").length}</div></Card>
        <Card className="p-5"><div className="text-xs text-muted-foreground">Out of Stock</div><div className="text-2xl font-bold mt-1 text-destructive">{products.filter(p => p.stock === "out").length}</div></Card>
      </div>

      <Card>
        <div className="p-4 border-b">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input placeholder="Search products..." className="pl-9 bg-muted/50 border-0" />
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
            {products.map((p) => (
              <TableRow key={p.id} className="hover:bg-muted/30">
                <TableCell>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center"><Package className="w-5 h-5 text-muted-foreground" /></div>
                    <div>
                      <div className="font-medium">{p.name}</div>
                      <div className="text-xs text-muted-foreground">{p.desc}</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="font-semibold">৳{p.price.toLocaleString()}</TableCell>
                <TableCell className="hidden md:table-cell">{stockBadge(p.stock)}</TableCell>
                <TableCell className="hidden lg:table-cell text-sm text-muted-foreground">{p.policy}</TableCell>
                <TableCell className="text-right"><Button variant="ghost" size="sm">Edit</Button></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
