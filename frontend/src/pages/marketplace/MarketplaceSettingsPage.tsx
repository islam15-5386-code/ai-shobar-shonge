import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

type MarketplaceSettings = {
  default_commission_rate: string;
  auto_approve_vendors: boolean;
  auto_approve_products: boolean;
  vendor_self_signup_enabled: boolean;
  require_vendor_kyc: boolean;
  min_payout_amount: string;
  default_payout_method: string;
  default_return_policy: string;
  default_delivery_policy: string;
  support_email: string;
  support_phone: string;
};

const defaults: MarketplaceSettings = {
  default_commission_rate: "10.00",
  auto_approve_vendors: false,
  auto_approve_products: false,
  vendor_self_signup_enabled: false,
  require_vendor_kyc: false,
  min_payout_amount: "1000.00",
  default_payout_method: "bank",
  default_return_policy: "",
  default_delivery_policy: "",
  support_email: "",
  support_phone: "",
};

export default function MarketplaceSettingsPage() {
  const [form, setForm] = useState<MarketplaceSettings>(defaults);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    try {
      setLoading(true);
      const data = await apiFetch<Partial<MarketplaceSettings>>("/api/marketplace/settings/");
      setForm({ ...defaults, ...(data || {}) });
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to load marketplace settings";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const save = async () => {
    try {
      setSaving(true);
      await apiFetch("/api/marketplace/settings/", {
        method: "PATCH",
        body: JSON.stringify({
          ...form,
          default_commission_rate: Number(form.default_commission_rate || 0),
          min_payout_amount: Number(form.min_payout_amount || 0),
        }),
      });
      toast.success("Marketplace settings saved");
    } catch (e) {
      const message = e instanceof Error ? e.message : "Save failed";
      toast.error(message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-4 md:p-8 space-y-4">
      <PageHeader
        title="Marketplace Settings"
        subtitle="Commission, policies and configuration"
        actions={<Button onClick={save} disabled={saving || loading}>{saving ? "Saving..." : "Save Settings"}</Button>}
      />

      <Card className="p-4 grid md:grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label>Default commission rate (%)</Label>
          <Input type="number" value={form.default_commission_rate} onChange={(e) => setForm((s) => ({ ...s, default_commission_rate: e.target.value }))} />
        </div>
        <div className="space-y-1">
          <Label>Minimum payout amount (BDT)</Label>
          <Input type="number" value={form.min_payout_amount} onChange={(e) => setForm((s) => ({ ...s, min_payout_amount: e.target.value }))} />
        </div>
        <div className="space-y-1">
          <Label>Default payout method</Label>
          <Input value={form.default_payout_method} onChange={(e) => setForm((s) => ({ ...s, default_payout_method: e.target.value }))} />
        </div>
        <div className="space-y-1">
          <Label>Support email</Label>
          <Input type="email" value={form.support_email} onChange={(e) => setForm((s) => ({ ...s, support_email: e.target.value }))} />
        </div>
        <div className="space-y-1 md:col-span-2">
          <Label>Support phone</Label>
          <Input value={form.support_phone} onChange={(e) => setForm((s) => ({ ...s, support_phone: e.target.value }))} />
        </div>
      </Card>

      <Card className="p-4 grid md:grid-cols-2 gap-3">
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.auto_approve_vendors} onChange={(e) => setForm((s) => ({ ...s, auto_approve_vendors: e.target.checked }))} />Auto-approve new vendors</label>
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.auto_approve_products} onChange={(e) => setForm((s) => ({ ...s, auto_approve_products: e.target.checked }))} />Auto-approve vendor products</label>
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.vendor_self_signup_enabled} onChange={(e) => setForm((s) => ({ ...s, vendor_self_signup_enabled: e.target.checked }))} />Allow vendor self-signup</label>
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.require_vendor_kyc} onChange={(e) => setForm((s) => ({ ...s, require_vendor_kyc: e.target.checked }))} />Require vendor KYC</label>
      </Card>

      <Card className="p-4 grid md:grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label>Default return policy</Label>
          <Textarea rows={5} value={form.default_return_policy} onChange={(e) => setForm((s) => ({ ...s, default_return_policy: e.target.value }))} />
        </div>
        <div className="space-y-1">
          <Label>Default delivery policy</Label>
          <Textarea rows={5} value={form.default_delivery_policy} onChange={(e) => setForm((s) => ({ ...s, default_delivery_policy: e.target.value }))} />
        </div>
      </Card>
    </div>
  );
}
