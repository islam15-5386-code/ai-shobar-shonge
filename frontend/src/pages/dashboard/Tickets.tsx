import { useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { tickets } from "@/lib/mockData";
import { Plus, MoreHorizontal, Bot } from "lucide-react";
import { toast } from "sonner";

const cols = [
  { key: "open", title: "Open", color: "bg-blue-500" },
  { key: "pending", title: "Pending", color: "bg-amber-500" },
  { key: "resolved", title: "Resolved", color: "bg-emerald-500" },
  { key: "closed", title: "Closed", color: "bg-slate-500" },
];

const priorityColor = (p: string) => p === "high" ? "bg-destructive/10 text-destructive border-destructive/20" : p === "medium" ? "bg-warning/10 text-warning border-warning/20" : "bg-muted text-muted-foreground";
const sentColor = (s: string) => s === "positive" ? "bg-success/10 text-success border-success/20" : s === "negative" ? "bg-destructive/10 text-destructive border-destructive/20" : "bg-muted text-muted-foreground";

export default function Tickets() {
  const [board, setBoard] = useState<{
    open: any[];
    pending: any[];
    resolved: any[];
    closed: any[];
  }>({
    open: [...tickets.open],
    pending: [...tickets.pending],
    resolved: [...tickets.resolved],
    closed: [...tickets.closed],
  });

  const customerPool = ["Rahim Ahmed", "Fatima Khan", "Karim Hossain", "Nusrat Jahan", "Tanvir Islam", "Sadia Rahman"];
  const sentimentPool = ["positive", "neutral", "negative"];
  const priorityPool = ["low", "medium", "high"];
  const ticketCounter = useMemo(
    () =>
      Math.max(
        ...Object.values(board)
          .flat()
          .map((t) => Number(String(t.id).replace("T-", "")) || 1000),
      ),
    [board],
  );

  const addTicket = (targetCol: "open" | "pending" | "resolved" | "closed", titleFromPrompt?: string | null) => {
    const titleInput = typeof titleFromPrompt === "string" ? titleFromPrompt : window.prompt("Ticket title লিখুন:");
    const title = (titleInput || "").trim();
    if (!title) {
      toast.error("Ticket title ছাড়া create করা যাবে না");
      return;
    }
    const nextId = `T-${ticketCounter + 1}`;
    const newTicket = {
      id: nextId,
      title,
      customer: customerPool[Math.floor(Math.random() * customerPool.length)],
      priority: priorityPool[Math.floor(Math.random() * priorityPool.length)],
      sentiment: sentimentPool[Math.floor(Math.random() * sentimentPool.length)],
      agent: "AI",
    };
    setBoard((prev) => ({ ...prev, [targetCol]: [newTicket, ...prev[targetCol]] }));
    toast.success(`${nextId} ticket "${targetCol}" column-এ add হয়েছে`);
  };

  const quickAction = (sourceCol: "open" | "pending" | "resolved" | "closed", ticket: any) => {
    const action = window.prompt(
      `Action for ${ticket.id}:\n1 = Move to Pending\n2 = Move to Resolved\n3 = Move to Closed\n4 = Delete`,
      "1",
    );
    if (!action) return;
    if (action === "4") {
      setBoard((prev) => ({ ...prev, [sourceCol]: prev[sourceCol].filter((t) => t.id !== ticket.id) }));
      toast.success(`${ticket.id} deleted`);
      return;
    }
    const map: Record<string, "pending" | "resolved" | "closed"> = { "1": "pending", "2": "resolved", "3": "closed" };
    const target = map[action];
    if (!target) return;
    setBoard((prev) => {
      const removed = prev[sourceCol].filter((t) => t.id !== ticket.id);
      const moved = { ...ticket };
      return { ...prev, [sourceCol]: removed, [target]: [moved, ...prev[target]] };
    });
    toast.success(`${ticket.id} moved to ${target}`);
  };

  return (
    <div className="p-4 md:p-8">
      <PageHeader
        title="Tickets"
        subtitle="Manage support requests across your team"
        actions={
          <Button className="gradient-primary border-0" onClick={() => addTicket("open")}>
            <Plus className="w-4 h-4 mr-1" /> New Ticket
          </Button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {cols.map((col) => (
          <div key={col.key} className="bg-muted/40 rounded-2xl p-3">
            <div className="flex items-center justify-between px-2 py-2 mb-2">
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${col.color}`} />
                <h3 className="font-semibold text-sm">{col.title}</h3>
                <Badge variant="outline" className="text-[10px] h-4 px-1.5">{(board as any)[col.key].length}</Badge>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="w-7 h-7"
                onClick={() => addTicket(col.key as "open" | "pending" | "resolved" | "closed")}
              >
                <Plus className="w-3.5 h-3.5" />
              </Button>
            </div>
            <div className="space-y-2">
              {(board as any)[col.key].map((t: any) => (
                <Card key={t.id} className="p-3.5 hover:shadow-md transition-all cursor-pointer hover:-translate-y-0.5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-mono text-muted-foreground">{t.id}</span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="w-6 h-6"
                      onClick={() => quickAction(col.key as "open" | "pending" | "resolved" | "closed", t)}
                    >
                      <MoreHorizontal className="w-3.5 h-3.5 text-muted-foreground" />
                    </Button>
                  </div>
                  <div className="font-medium text-sm mb-3 leading-snug">{t.title}</div>
                  <div className="flex items-center gap-1.5 mb-3 flex-wrap">
                    <Badge variant="outline" className={`text-[10px] h-5 ${priorityColor(t.priority)}`}>{t.priority}</Badge>
                    <Badge variant="outline" className={`text-[10px] h-5 ${sentColor(t.sentiment)}`}>{t.sentiment}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="text-xs text-muted-foreground">{t.customer}</div>
                    {t.agent === "AI" ? (
                      <Badge variant="outline" className="text-[10px] h-5 bg-primary/5 border-primary/20"><Bot className="w-2.5 h-2.5 mr-1" /> AI</Badge>
                    ) : (
                      <Avatar className="w-6 h-6"><AvatarFallback className="text-[10px] gradient-primary text-white">{t.agent[0]}</AvatarFallback></Avatar>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
