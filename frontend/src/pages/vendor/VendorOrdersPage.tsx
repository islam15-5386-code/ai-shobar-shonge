import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";

export default function VendorOrdersPage() { const [rows,setRows]=useState<any[]>([]); useEffect(()=>{apiFetch<any[]>('/api/vendor/orders/').then(setRows).catch(()=>setRows([]));},[]); return <div className="p-4 md:p-8 space-y-4"><PageHeader title="Vendor Orders" subtitle="Track your own orders" /><Card className="p-4 space-y-2">{rows.map(r=><div key={r.id} className="border rounded p-3"><div className="font-medium">{r.order_number}</div><div className="text-xs text-muted-foreground">{r.status} · {r.total}</div></div>)}</Card></div>; }
