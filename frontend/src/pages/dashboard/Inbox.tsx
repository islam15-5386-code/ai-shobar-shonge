import { FormEvent, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { conversations, customerOrderHistory, messages, type OrderTrackingStage } from "@/lib/mockData";
import { Search, Send, Paperclip, Smile, UserPlus, Ticket, CheckCircle2, Hand, Bot, Sparkles, Phone, Mail, MapPin } from "lucide-react";
import { toast } from "sonner";

export default function Inbox() {
  const [active, setActive] = useState(conversations[0]);
  const [draft, setDraft] = useState("");
  const [isTakenOver, setIsTakenOver] = useState(false);
  const [isAssigned, setIsAssigned] = useState(false);
  const [isResolved, setIsResolved] = useState(false);
  const [createdTicketId, setCreatedTicketId] = useState<number | null>(null);
  const [threads, setThreads] = useState<Record<string, typeof messages>>(() => {
    const initial: Record<string, typeof messages> = {};
    conversations.forEach((c, idx) => {
      initial[c.id] = messages.map((m, mIdx) => ({
        ...m,
        time: m.time,
        text: idx === 0 ? m.text : mIdx % 2 === 0 ? `${c.name}: ${m.text}` : m.text,
      }));
    });
    return initial;
  });

  const sentimentColor = (s: string) =>
    s === "positive"
      ? "bg-success/10 text-success border-success/20"
      : s === "negative"
        ? "bg-destructive/10 text-destructive border-destructive/20"
        : "bg-muted text-muted-foreground";

  const activeMessages = useMemo(() => threads[active.id] || [], [threads, active.id]);
  const activeOrders = useMemo(() => customerOrderHistory[active.id] || [], [active.id]);

  const trackingStep = (status: OrderTrackingStage) => {
    const map: Record<OrderTrackingStage, number> = {
      confirmed: 1,
      packed: 2,
      shipped: 3,
      out_for_delivery: 4,
      delivered: 5,
      cancelled: 0,
    };
    return map[status];
  };

  const trackingLabel = (status: OrderTrackingStage) => {
    const map: Record<OrderTrackingStage, string> = {
      confirmed: "Confirmed",
      packed: "Packed",
      shipped: "Shipped",
      out_for_delivery: "Out for delivery",
      delivered: "Delivered",
      cancelled: "Cancelled",
    };
    return map[status];
  };

  const handleTakeOver = () => {
    setIsTakenOver(true);
    toast.success(`Conversation with ${active.name} is now under human control`);
  };

  const handleAssign = () => {
    setIsAssigned(true);
    toast.success(`Assigned ${active.name}'s conversation to current agent`);
  };

  const handleCreateTicket = () => {
    if (createdTicketId) {
      toast.message(`Ticket #${createdTicketId} already created`);
      return;
    }
    const ticketId = Math.floor(Math.random() * 9000) + 1000;
    setCreatedTicketId(ticketId);
    toast.success(`Ticket #${ticketId} created for ${active.name}`);
  };

  const handleResolve = () => {
    setIsResolved(true);
    toast.success(`Conversation with ${active.name} marked as resolved`);
  };

  const handleSend = (e: FormEvent) => {
    e.preventDefault();
    const text = draft.trim();
    if (!text) return;
    const now = new Date();
    const hh = String(now.getHours() % 12 || 12).padStart(2, "0");
    const mm = String(now.getMinutes()).padStart(2, "0");
    const time = `${hh}:${mm} ${now.getHours() >= 12 ? "PM" : "AM"}`;
    setThreads((prev) => ({
      ...prev,
      [active.id]: [...(prev[active.id] || []), { from: "agent", text, time }],
    }));
    setDraft("");
  };

  return (
    <div className="h-[calc(100vh-4rem)] grid lg:grid-cols-[320px_1fr_320px] grid-cols-1">
      <div className="border-r flex flex-col bg-card">
        <div className="p-4 border-b">
          <h2 className="font-bold text-lg mb-3">Live Inbox</h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input placeholder="Search conversations..." className="pl-9 bg-muted/50 border-0" />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => setActive(c)}
              className={`w-full flex gap-3 p-4 border-b text-left hover:bg-muted/50 transition ${active.id === c.id ? "bg-primary/5 border-l-2 border-l-primary" : ""}`}
            >
              <Avatar className="w-10 h-10"><AvatarFallback className="gradient-primary text-white text-xs">{c.avatar}</AvatarFallback></Avatar>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-sm truncate">{c.name}</span>
                  <span className="text-[10px] text-muted-foreground">{c.time}</span>
                </div>
                <div className="text-xs text-muted-foreground truncate font-bangla mt-0.5">{c.message}</div>
                <div className="flex items-center gap-1.5 mt-1.5">
                  <Badge variant="outline" className="text-[10px] h-4 px-1.5">{c.channel}</Badge>
                  {c.unread > 0 && <Badge className="bg-primary text-primary-foreground text-[10px] h-4 px-1.5">{c.unread}</Badge>}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-col bg-muted/20">
        <div className="h-16 border-b bg-card flex items-center justify-between px-5">
          <div className="flex items-center gap-3">
            <Avatar><AvatarFallback className="gradient-primary text-white">{active.avatar}</AvatarFallback></Avatar>
            <div>
              <div className="font-semibold text-sm">{active.name}</div>
              <div className="text-xs text-muted-foreground flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-success" /> Active now · {active.channel}</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline" onClick={handleTakeOver}><Hand className="w-3.5 h-3.5 mr-1" /> {isTakenOver ? "Taken Over" : "Take Over"}</Button>
            <Button size="sm" variant="outline" className="hidden md:inline-flex" onClick={handleAssign}><UserPlus className="w-3.5 h-3.5 mr-1" /> {isAssigned ? "Assigned" : "Assign"}</Button>
            <Button size="sm" variant="outline" className="hidden md:inline-flex" onClick={handleCreateTicket}><Ticket className="w-3.5 h-3.5 mr-1" /> {createdTicketId ? `Ticket #${createdTicketId}` : "Ticket"}</Button>
            <Button size="sm" className="gradient-primary border-0" onClick={handleResolve}><CheckCircle2 className="w-3.5 h-3.5 mr-1" /> {isResolved ? "Resolved" : "Resolve"}</Button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-3">
          {activeMessages.map((m, i) => (
            <div key={i} className={`flex ${m.from === "customer" ? "justify-start" : "justify-end"}`}>
              <div className="max-w-md">
                <div className={`px-4 py-2.5 rounded-2xl text-sm font-bangla ${m.from === "customer" ? "bg-card rounded-tl-sm border" : "gradient-primary text-primary-foreground rounded-tr-sm shadow-md"}`}>{m.text}</div>
                <div className={`text-[10px] text-muted-foreground mt-1 px-1 flex items-center gap-1 ${m.from === "customer" ? "" : "justify-end"}`}>
                  {m.from === "ai" && <Bot className="w-3 h-3" />} {m.time}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 bg-card border-t">
          <form onSubmit={handleSend} className="flex items-center gap-2 bg-muted/50 rounded-xl px-3 py-2">
            <Button size="icon" variant="ghost" className="w-8 h-8"><Paperclip className="w-4 h-4" /></Button>
            <Input placeholder="Type your message... / use AI suggestions" className="border-0 bg-transparent focus-visible:ring-0" value={draft} onChange={(e) => setDraft(e.target.value)} />
            <Button size="icon" variant="ghost" className="w-8 h-8"><Smile className="w-4 h-4" /></Button>
            <Button type="submit" size="icon" className="gradient-primary border-0 w-9 h-9"><Send className="w-4 h-4" /></Button>
          </form>
        </div>
      </div>

      <div className="border-l bg-card hidden lg:flex flex-col overflow-y-auto">
        <div className="p-6 text-center border-b">
          <Avatar className="w-20 h-20 mx-auto mb-3"><AvatarFallback className="gradient-primary text-white text-xl">{active.avatar}</AvatarFallback></Avatar>
          <h3 className="font-bold">{active.name}</h3>
          <Badge variant="outline" className={`mt-2 ${sentimentColor(active.sentiment)}`}>{active.sentiment} sentiment</Badge>
        </div>
        <div className="p-5 space-y-3 border-b text-sm">
          <div className="flex items-center gap-2 text-muted-foreground"><Phone className="w-4 h-4" /> +8801712345678</div>
          <div className="flex items-center gap-2 text-muted-foreground"><Mail className="w-4 h-4" /> {active.name.toLowerCase().replace(" ", ".")}@gmail.com</div>
          <div className="flex items-center gap-2 text-muted-foreground"><MapPin className="w-4 h-4" /> Dhanmondi, Dhaka</div>
        </div>
        <div className="p-5 border-b">
          <div className="flex items-center gap-2 mb-3"><Sparkles className="w-4 h-4 text-primary" /><h4 className="font-semibold text-sm">AI Insights</h4></div>
          <Card className="p-3 bg-primary/5 border-primary/10 text-xs space-y-2">
            <div><strong>Intent:</strong> Product inquiry → Purchase</div>
            <div><strong>Confidence:</strong> 94%</div>
            <div><strong>Suggested:</strong> Offer free home delivery</div>
          </Card>
        </div>
        <div className="p-5">
          <h4 className="font-semibold text-sm mb-3">Order History</h4>
          {activeOrders.length === 0 ? (
            <Card className="p-3 text-xs text-muted-foreground">No order history for this customer yet.</Card>
          ) : (
            <div className="space-y-2 text-xs">
              {activeOrders.map((o) => {
                const step = trackingStep(o.status);
                const progress = o.status === "cancelled" ? 100 : Math.round((step / 5) * 100);
                return (
                  <Card key={o.orderId} className="p-3">
                    <div className="flex items-center justify-between gap-2">
                      <div className="font-medium">Order #{o.orderId}</div>
                      <Badge variant="outline">{trackingLabel(o.status)}</Badge>
                    </div>
                    <div className="text-muted-foreground mt-1">৳{o.amountBdt.toLocaleString()} · {o.items}</div>
                    <div className="text-muted-foreground mt-1">Courier: {o.courier} · ETA: {o.eta}</div>
                    <div className="text-muted-foreground mt-1">Tracking: {o.trackingCode} · Updated: {o.updatedAt}</div>
                    <div className="h-1.5 bg-muted rounded-full mt-2 overflow-hidden">
                      <div className={`${o.status === "cancelled" ? "bg-destructive" : "bg-primary"} h-full`} style={{ width: `${progress}%` }} />
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
