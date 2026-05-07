import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";

export default function VendorSettingsPage() {
  const [data, setData] = useState<any>({ name: "", support_email: "", support_phone: "", address: "" });
  useEffect(()=>{apiFetch<any>('/api/vendor/settings/').then(setData).catch(()=>{});},[]);
  const save = async () => { await apiFetch('/api/vendor/settings/', { method:'PATCH', body: JSON.stringify(data) }); };
  return <div className="p-4 md:p-8 space-y-4"><PageHeader title="Vendor Settings" subtitle="Update vendor profile" /><Card className="p-4 space-y-2"><Input placeholder="Name" value={data.name||''} onChange={e=>setData((p:any)=>({...p,name:e.target.value}))}/><Input placeholder="Support email" value={data.support_email||''} onChange={e=>setData((p:any)=>({...p,support_email:e.target.value}))}/><Input placeholder="Support phone" value={data.support_phone||''} onChange={e=>setData((p:any)=>({...p,support_phone:e.target.value}))}/><Input placeholder="Address" value={data.address||''} onChange={e=>setData((p:any)=>({...p,address:e.target.value}))}/><Button onClick={save}>Save</Button></Card></div>;
}
