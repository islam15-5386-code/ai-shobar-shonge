import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";

export default function VendorDashboardPage() {
  const [data, setData] = useState<any>(null);
  useEffect(() => { apiFetch('/api/vendor/dashboard/').then(setData).catch(()=>setData(null)); }, []);
  return <div className="p-4 md:p-8 space-y-4"><PageHeader title="Vendor Dashboard" subtitle="Your vendor business metrics" /><Card className="p-4 grid md:grid-cols-3 gap-3 text-sm">{['total_orders','pending_orders','delivered_orders','total_sales','vendor_earnings','open_tickets'].map(k=><div key={k} className="border rounded p-3"><div className="text-muted-foreground">{k.replace('_',' ')}</div><div className="font-semibold">{data?.[k] ?? '-'}</div></div>)}</Card></div>;
}
