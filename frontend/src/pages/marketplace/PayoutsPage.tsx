import { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

type Vendor = { id: number; name: string };

type Payout = {
  id: number;
  vendor: number;
  amount: string;
  status: string;
  payout_method?: string;
  transaction_reference?: string;
  requested_at?: string;
  paid_at?: string | null;
};

const statusClass = (s: string) => {
  if (s === "paid") return "bg-success/10 text-success border-success/20";
  if (s === "processing") return "bg-warning/10 text-warning border-warning/20";
  if (s === "failed") return "bg-destructive/10 text-destructive border-destructive/20";
  return "";
};

export default function PayoutsPage() {
  const [rows, setRows] = useState<Payout[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [vendorId, setVendorId] = useState("");
  const [amount, setAmount] = useState("");
  const [payoutMethod, setPayoutMethod] = useState("bank");
  const [transactionRef, setTransactionRef] = useState("");
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [payingId, setPayingId] = useState<number | null>(null);

  const vendorMap = useMemo(() => {
    const m = new Map<number, string>();
    vendors.forEach((v) => m.set(v.id, v.name));
    return m;
  }, [vendors]);

  const load = async () => {
    try {
      setLoading(true);
      const [payoutsRes, vendorsRes] = await Promise.all([
        apiFetch<Payout[]>("/api/marketplace/payouts/"),
        apiFetch<any[]>("/api/vendors/"),
      ]);
      setRows(payoutsRes || []);
      setVendors((vendorsRes || []).map((v) => ({ id: v.id, name: v.name })));
      if (!vendorId && vendorsRes?.length) setVendorId(String(vendorsRes[0].id));
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to load payouts";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const create = async () => {
    if (!vendorId) {
      toast.error("Please select a vendor");
      return;
    }
    const amt = Number(amount);
    if (!Number.isFinite(amt) || amt <= 0) {
      toast.error("Amount must be greater than 0");
      return;
    }
    try {
      setCreating(true);
      await apiFetch("/api/marketplace/payouts/", {
        method: "POST",
        body: JSON.stringify({
          vendor_id: Number(vendorId),
          amount: amt,
          payout_method: payoutMethod,
          transaction_reference: transactionRef.trim(),
        }),
      });
      setAmount("");
      setTransactionRef("");
      toast.success("Payout created");
      await load();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Create payout failed";
      toast.error(message);
    } finally {
      setCreating(false);
    }
  };

  const markPaid = async (id: number) => {
    try {
      setPayingId(id);
      await apiFetch(`/api/marketplace/payouts/${id}/mark-paid/`, {
        method: "PATCH",
        body: JSON.stringify({ transaction_reference: transactionRef.trim() || `TX-${Date.now()}` }),
      });
      toast.success("Payout marked paid");
      await load();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Mark paid failed";
      toast.error(message);
    } finally {
      setPayingId(null);
    }
  };

  const exportCsv = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const base = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
      const res = await fetch(`${base}/api/marketplace/payouts/export/`, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (!res.ok) throw new Error(await res.text());
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "vendor_payouts.csv";
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
        title="Payouts"
        subtitle="Vendor payout management"
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={load} disabled={loading}>{loading ? "Loading..." : "Refresh"}</Button>
            <Button onClick={exportCsv}>Export CSV</Button>
          </div>
        }
      />

      <Card className="p-4 grid md:grid-cols-5 gap-2">
        <Select value={vendorId} onValueChange={setVendorId}>
          <SelectTrigger className="md:col-span-2"><SelectValue placeholder="Select vendor" /></SelectTrigger>
          <SelectContent>
            {vendors.map((v) => (
              <SelectItem key={v.id} value={String(v.id)}>{v.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Input className="md:col-span-1" placeholder="Amount" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
        <Input className="md:col-span-1" placeholder="Transaction ref (optional)" value={transactionRef} onChange={(e) => setTransactionRef(e.target.value)} />
        <Button className="md:col-span-1" onClick={create} disabled={creating}>{creating ? "Creating..." : "Create"}</Button>
      </Card>

      <Card className="p-4 space-y-2">
        {rows.map((r) => (
          <div key={r.id} className="border rounded p-3 flex flex-wrap items-center justify-between gap-2">
            <div>
              <div className="font-medium">{vendorMap.get(r.vendor) || `Vendor #${r.vendor}`}</div>
              <div className="text-xs text-muted-foreground">
                ৳{Number(r.amount || 0).toLocaleString()} · {r.payout_method || "bank"} · {r.transaction_reference || "-"}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className={statusClass(r.status)}>{r.status}</Badge>
              {r.status !== "paid" && (
                <Button variant="outline" size="sm" onClick={() => markPaid(r.id)} disabled={payingId === r.id}>
                  {payingId === r.id ? "Updating..." : "Mark Paid"}
                </Button>
              )}
            </div>
          </div>
        ))}
        {!loading && rows.length === 0 && <div className="text-sm text-muted-foreground py-8 text-center">No payouts found.</div>}
      </Card>
    </div>
  );
}
