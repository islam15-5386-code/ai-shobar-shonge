import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";

export default function CommissionsPage() {
  const [rows, setRows] = useState<any[]>([]);
  useEffect(() => { apiFetch<any[]>("/api/marketplace/commissions/").then(setRows).catch(()=>setRows([])); }, []);
  return <div className="p-4 md:p-8 space-y-4"><PageHeader title="Commissions" subtitle="Per-order marketplace commission" /><Card className="p-4 space-y-2">{rows.map(r=><div key={r.id} className="border rounded p-3"><div className="font-medium">Order #{r.order}</div><div className="text-xs text-muted-foreground">Commission: {r.commission_amount} · Earning: {r.vendor_earning}</div></div>)}</Card></div>;
}
