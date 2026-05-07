import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

export default function VendorsPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [name, setName] = useState("");

  const load = async () => {
    const data = await apiFetch<any[]>("/api/vendors/");
    setRows(data || []);
  };

  useEffect(() => {
    load().catch(() => toast.error("Failed to load vendors"));
  }, []);

  const add = async () => {
    if (!name.trim()) return;
    try {
      await apiFetch("/api/vendors/", {
        method: "POST",
        body: JSON.stringify({
          name: name.trim(),
          slug: name.toLowerCase().trim().replace(/\s+/g, "-"),
        }),
      });
      setName("");
      await load();
      toast.success("Vendor added");
    } catch (e) {
      const message = e instanceof Error ? e.message : "Add vendor failed";
      toast.error(message);
    }
  };

  return (
    <div className="p-4 md:p-8 space-y-4">
      <PageHeader title="Vendors" subtitle="Manage marketplace vendors" />
      <Card className="p-4 flex gap-2">
        <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Vendor name" />
        <Button onClick={add}>Add Vendor</Button>
      </Card>
      <Card className="p-4 space-y-2">
        {rows.map((v) => (
          <div key={v.id} className="border rounded p-3 flex justify-between">
            <div>
              <div className="font-medium">{v.name}</div>
              <div className="text-xs text-muted-foreground">{v.status} - {v.city || "-"}</div>
            </div>
          </div>
        ))}
      </Card>
    </div>
  );
}
