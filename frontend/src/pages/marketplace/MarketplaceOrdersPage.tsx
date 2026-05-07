import { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

type OrderItem = {
  id: number;
  order_number: string;
  status: string;
  payment_status: string;
  total: string;
  currency: string;
  created_at: string;
};

const statusOptions = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "refunded"];

export default function MarketplaceOrdersPage() {
  const [rows, setRows] = useState<OrderItem[]>([]);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  const [payment, setPayment] = useState("all");
  const [loading, setLoading] = useState(false);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const load = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (status !== "all") params.set("status", status);
      if (payment !== "all") params.set("payment", payment);
      const qs = params.toString() ? `?${params.toString()}` : "";
      const data = await apiFetch<OrderItem[]>(`/api/marketplace/orders/${qs}`);
      setRows(data || []);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to load marketplace orders";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [status, payment]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((o) =>
      String(o.order_number || "").toLowerCase().includes(q) ||
      String(o.status || "").toLowerCase().includes(q) ||
      String(o.payment_status || "").toLowerCase().includes(q)
    );
  }, [rows, query]);

  const updateStatus = async (orderId: number, nextStatus: string) => {
    try {
      setUpdatingId(orderId);
      await apiFetch(`/api/marketplace/orders/${orderId}/status/`, {
        method: "PATCH",
        body: JSON.stringify({ status: nextStatus }),
      });
      toast.success("Order status updated");
      await load();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Status update failed";
      toast.error(message);
    } finally {
      setUpdatingId(null);
    }
  };

  const createDemoOrder = async () => {
    try {
      await apiFetch("/api/marketplace/orders/demo-create/", { method: "POST", body: JSON.stringify({}) });
      toast.success("Demo order created");
      await load();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Demo order create failed";
      toast.error(message);
    }
  };

  const exportCsv = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${(import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/+$/, "")}/api/marketplace/orders/export/`, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (!res.ok) throw new Error(await res.text());
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "marketplace_orders.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success("CSV exported");
    } catch (e) {
      const message = e instanceof Error ? e.message : "Export failed";
      toast.error(message);
    }
  };

  return (
    <div className="p-4 md:p-8 space-y-4">
      <PageHeader
        title="Marketplace Orders"
        subtitle="All vendor orders"
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={load} disabled={loading}>{loading ? "Loading..." : "Refresh"}</Button>
            <Button variant="outline" onClick={createDemoOrder}>Create Demo Order</Button>
            <Button onClick={exportCsv}>Export CSV</Button>
          </div>
        }
      />

      <Card className="p-4 flex flex-wrap gap-2">
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search order no / status" className="max-w-sm" />
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All status</SelectItem>
            {statusOptions.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={payment} onValueChange={setPayment}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Payment" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All payment</SelectItem>
            <SelectItem value="unpaid">unpaid</SelectItem>
            <SelectItem value="paid">paid</SelectItem>
            <SelectItem value="failed">failed</SelectItem>
            <SelectItem value="refunded">refunded</SelectItem>
          </SelectContent>
        </Select>
      </Card>

      <Card className="p-4 space-y-2">
        {filtered.map((o) => (
          <div key={o.id} className="border rounded p-3 flex flex-wrap gap-3 items-center justify-between">
            <div>
              <div className="font-medium">{o.order_number}</div>
              <div className="text-xs text-muted-foreground">
                {o.status} · {o.payment_status} · {o.currency} {o.total}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{o.status}</Badge>
              <select
                className="h-9 rounded-md border px-2"
                value={o.status}
                onChange={(e) => updateStatus(o.id, e.target.value)}
                disabled={updatingId === o.id}
              >
                {statusOptions.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>
        ))}
        {!loading && filtered.length === 0 && <div className="text-sm text-muted-foreground py-8 text-center">No orders found.</div>}
      </Card>
    </div>
  );
}
