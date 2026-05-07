import { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { Check, Sparkles } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

type Plan = {
  id: number;
  code: string;
  name: string;
  monthly_price: string;
  message_limit: number;
  seat_limit: number;
  channels_allowed?: string[];
};

type CurrentPayload = {
  subscription?: {
    id: number;
    status: string;
    plan: { id: number; code: string; name: string };
  } | null;
  usage?: {
    quantity: number;
    limit: number | null;
    remaining: number | null;
  } | null;
};

type Invoice = {
  id: number;
  invoice_number: string;
  amount: string;
  currency: string;
  status: string;
};

const fmtBDT = (v: string | number) =>
  `৳${Number(v || 0).toLocaleString("en-BD", { maximumFractionDigits: 0 })}`;

export default function Billing() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [current, setCurrent] = useState<CurrentPayload | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [payingPlanId, setPayingPlanId] = useState<number | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<"sandbox_card" | "sandbox_bkash" | "sandbox_nagad">(
    "sandbox_card"
  );

  const load = async () => {
    setLoading(true);
    try {
      const [planRows, currentRow, invoiceRows] = await Promise.all([
        apiFetch<Plan[]>("/api/billing/plans/"),
        apiFetch<CurrentPayload>("/api/billing/current/"),
        apiFetch<Invoice[]>("/api/billing/invoices/"),
      ]);
      setPlans(planRows || []);
      setCurrent(currentRow || null);
      setInvoices(invoiceRows || []);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to load billing";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const currentPlanId = current?.subscription?.plan?.id ?? null;
  const usage = current?.usage;
  const usageLimit = usage?.limit ?? null;
  const usageQty = usage?.quantity ?? 0;
  const usagePct = useMemo(() => {
    if (!usageLimit || usageLimit <= 0) return 0;
    return Math.max(0, Math.min(100, Math.round((usageQty / usageLimit) * 100)));
  }, [usageLimit, usageQty]);

  const handleSandboxPay = async (planId: number) => {
    try {
      setPayingPlanId(planId);
      try {
        const res = await apiFetch<{ detail: string; transaction_reference: string }>("/api/billing/sandbox/checkout/", {
          method: "POST",
          body: JSON.stringify({ plan_id: planId, payment_method: paymentMethod }),
        });
        toast.success(`${res.detail} (${res.transaction_reference})`);
      } catch {
        await apiFetch("/api/billing/subscription/", {
          method: "POST",
          body: JSON.stringify({ plan_id: planId, status: "active", cancel_at_period_end: false }),
        });
        toast.success("Subscription updated");
      }
      await load();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Sandbox payment failed";
      toast.error(message);
    } finally {
      setPayingPlanId(null);
    }
  };

  const currentPlan = plans.find((p) => p.id === currentPlanId) || null;

  return (
    <div className="p-4 md:p-8">
      <PageHeader title="Billing & Plans" subtitle="Manage your subscription and usage" />

      <Card className="p-6 mb-6 gradient-primary text-white border-0 shadow-elegant">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <Badge className="bg-white/20 text-white border-0 mb-2">Current Plan</Badge>
            <h2 className="text-3xl font-bold">{currentPlan?.name || "No Plan"}</h2>
            <p className="text-white/80 text-sm mt-1">
              {currentPlan ? `${fmtBDT(currentPlan.monthly_price)} / month` : "No active subscription"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value as any)}
              className="bg-white text-slate-800 rounded-md border px-3 py-2 text-sm"
            >
              <option value="sandbox_card">Sandbox Card</option>
              <option value="sandbox_bkash">Sandbox bKash</option>
              <option value="sandbox_nagad">Sandbox Nagad</option>
            </select>
            <Button
              variant="outline"
              className="bg-white text-primary hover:bg-white/90 border-0"
              disabled={!currentPlanId || payingPlanId === currentPlanId}
              onClick={() => currentPlanId && handleSandboxPay(currentPlanId)}
            >
              {payingPlanId === currentPlanId ? "Processing..." : "Manage subscription"}
            </Button>
          </div>
        </div>
      </Card>

      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <Card className="p-5">
          <div className="text-xs text-muted-foreground">Conversations</div>
          <div className="text-2xl font-bold mt-1">
            {usageQty.toLocaleString()}{" "}
            <span className="text-base text-muted-foreground font-normal">/ {usageLimit?.toLocaleString() || "-"}</span>
          </div>
          <div className="h-2 bg-muted rounded-full mt-3 overflow-hidden">
            <div className="h-full gradient-primary" style={{ width: `${usagePct}%` }} />
          </div>
          <div className="text-xs text-muted-foreground mt-2">{usagePct}% used</div>
        </Card>
        <Card className="p-5">
          <div className="text-xs text-muted-foreground">Billing status</div>
          <div className="text-2xl font-bold mt-1">{current?.subscription?.status || "inactive"}</div>
          <div className="text-xs text-muted-foreground mt-2">Sandbox mode enabled</div>
        </Card>
        <Card className="p-5">
          <div className="text-xs text-muted-foreground">Last invoice</div>
          <div className="text-2xl font-bold mt-1">{invoices[0] ? fmtBDT(invoices[0].amount) : "৳0"}</div>
          <div className="text-xs text-muted-foreground mt-2">{invoices[0]?.invoice_number || "No invoice yet"}</div>
        </Card>
      </div>

      <h3 className="font-bold text-xl mb-4">Compare plans</h3>
      <div className="grid md:grid-cols-3 gap-4">
        {plans.map((p) => {
          const price = Number(p.monthly_price || 0);
          const isCurrent = p.id === currentPlanId;
          return (
            <Card key={p.id} className={`p-6 relative ${isCurrent ? "ring-2 ring-primary shadow-elegant" : ""}`}>
              {isCurrent && (
                <Badge className="absolute -top-3 left-6 gradient-primary border-0">
                  <Sparkles className="w-3 h-3 mr-1" />
                  Current
                </Badge>
              )}
              <h4 className="font-bold text-lg">{p.name}</h4>
              <div className="my-4">
                <span className="text-3xl font-extrabold">{fmtBDT(price)}</span>
                <span className="text-muted-foreground">/mo</span>
              </div>
              <ul className="space-y-2 text-sm mb-6">
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-success flex-shrink-0 mt-0.5" />
                  {p.message_limit.toLocaleString()} conversations/mo
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-success flex-shrink-0 mt-0.5" />
                  {p.seat_limit} seats
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-success flex-shrink-0 mt-0.5" />
                  Channels: {(p.channels_allowed || []).join(", ") || "website"}
                </li>
              </ul>
              <Button
                className={`w-full ${isCurrent ? "" : "gradient-primary border-0"}`}
                variant={isCurrent ? "outline" : "default"}
                disabled={isCurrent || payingPlanId === p.id || loading}
                onClick={() => handleSandboxPay(p.id)}
              >
                {isCurrent ? "Current plan" : payingPlanId === p.id ? "Processing..." : price > Number(currentPlan?.monthly_price || 0) ? "Upgrade" : "Downgrade"}
              </Button>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
