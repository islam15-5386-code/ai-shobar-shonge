import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { Check, Sparkles } from "lucide-react";

const plans = [
  { name: "Starter", price: 1499, features: ["1,000 conversations/mo", "Messenger only", "Basic AI", "Email support"], current: false },
  { name: "Pro", price: 4999, features: ["15,000 conversations/mo", "All channels", "Bangla + English AI", "Ticket management", "Priority support"], current: true },
  { name: "Business", price: 14999, features: ["Unlimited conversations", "Custom AI training", "Multiple agents", "API access", "Dedicated manager"], current: false },
];

export default function Billing() {
  return (
    <div className="p-4 md:p-8">
      <PageHeader title="Billing & Plans" subtitle="Manage your subscription and usage" />

      <Card className="p-6 mb-6 gradient-primary text-white border-0 shadow-elegant">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <Badge className="bg-white/20 text-white border-0 mb-2">Current Plan</Badge>
            <h2 className="text-3xl font-bold">Pro Plan</h2>
            <p className="text-white/80 text-sm mt-1">৳4,999 / month · Renews Jun 5, 2026</p>
          </div>
          <Button variant="outline" className="bg-white text-primary hover:bg-white/90 border-0">Manage subscription</Button>
        </div>
      </Card>

      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <Card className="p-5">
          <div className="text-xs text-muted-foreground">Conversations</div>
          <div className="text-2xl font-bold mt-1">9,421 <span className="text-base text-muted-foreground font-normal">/ 15,000</span></div>
          <div className="h-2 bg-muted rounded-full mt-3 overflow-hidden"><div className="h-full gradient-primary" style={{ width: "63%" }} /></div>
          <div className="text-xs text-muted-foreground mt-2">63% used · Resets in 12 days</div>
        </Card>
        <Card className="p-5">
          <div className="text-xs text-muted-foreground">AI Tokens</div>
          <div className="text-2xl font-bold mt-1">2.4M <span className="text-base text-muted-foreground font-normal">/ 5M</span></div>
          <div className="h-2 bg-muted rounded-full mt-3 overflow-hidden"><div className="h-full bg-accent" style={{ width: "48%" }} /></div>
          <div className="text-xs text-muted-foreground mt-2">48% used</div>
        </Card>
        <Card className="p-5">
          <div className="text-xs text-muted-foreground">Active agents</div>
          <div className="text-2xl font-bold mt-1">3 <span className="text-base text-muted-foreground font-normal">/ 5</span></div>
          <div className="h-2 bg-muted rounded-full mt-3 overflow-hidden"><div className="h-full bg-warning" style={{ width: "60%" }} /></div>
          <div className="text-xs text-muted-foreground mt-2">2 seats available</div>
        </Card>
      </div>

      <h3 className="font-bold text-xl mb-4">Compare plans</h3>
      <div className="grid md:grid-cols-3 gap-4">
        {plans.map((p) => (
          <Card key={p.name} className={`p-6 relative ${p.current ? "ring-2 ring-primary shadow-elegant" : ""}`}>
            {p.current && <Badge className="absolute -top-3 left-6 gradient-primary border-0"><Sparkles className="w-3 h-3 mr-1" />Current</Badge>}
            <h4 className="font-bold text-lg">{p.name}</h4>
            <div className="my-4"><span className="text-3xl font-extrabold">৳{p.price.toLocaleString()}</span><span className="text-muted-foreground">/mo</span></div>
            <ul className="space-y-2 text-sm mb-6">
              {p.features.map((f) => <li key={f} className="flex items-start gap-2"><Check className="w-4 h-4 text-success flex-shrink-0 mt-0.5" />{f}</li>)}
            </ul>
            <Button className={`w-full ${p.current ? "" : "gradient-primary border-0"}`} variant={p.current ? "outline" : "default"} disabled={p.current}>
              {p.current ? "Current plan" : p.price > 4999 ? "Upgrade" : "Downgrade"}
            </Button>
          </Card>
        ))}
      </div>
    </div>
  );
}
