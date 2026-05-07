import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";

export default function VendorProductsPage() { const [rows,setRows]=useState<any[]>([]); useEffect(()=>{apiFetch<any[]>('/api/vendor/products/').then(setRows).catch(()=>setRows([]));},[]); return <div className="p-4 md:p-8 space-y-4"><PageHeader title="Vendor Products" subtitle="Manage your own products" /><Card className="p-4 space-y-2">{rows.map(r=><div key={r.id} className="border rounded p-3"><div className="font-medium">{r.name}</div><div className="text-xs text-muted-foreground">{r.price} · {r.approval_status}</div></div>)}</Card></div>; }
