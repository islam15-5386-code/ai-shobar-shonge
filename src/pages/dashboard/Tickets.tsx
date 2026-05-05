import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { tickets } from "@/lib/mockData";
import { Plus, MoreHorizontal, Bot } from "lucide-react";

const cols = [
  { key: "open", title: "Open", color: "bg-blue-500" },
  { key: "pending", title: "Pending", color: "bg-amber-500" },
  { key: "resolved", title: "Resolved", color: "bg-emerald-500" },
  { key: "closed", title: "Closed", color: "bg-slate-500" },
];

const priorityColor = (p: string) => p === "high" ? "bg-destructive/10 text-destructive border-destructive/20" : p === "medium" ? "bg-warning/10 text-warning border-warning/20" : "bg-muted text-muted-foreground";
const sentColor = (s: string) => s === "positive" ? "bg-success/10 text-success border-success/20" : s === "negative" ? "bg-destructive/10 text-destructive border-destructive/20" : "bg-muted text-muted-foreground";

export default function Tickets() {
  return (
    <div className="p-4 md:p-8">
      <PageHeader title="Tickets" subtitle="Manage support requests across your team" actions={<Button className="gradient-primary border-0"><Plus className="w-4 h-4 mr-1" /> New Ticket</Button>} />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {cols.map((col) => (
          <div key={col.key} className="bg-muted/40 rounded-2xl p-3">
            <div className="flex items-center justify-between px-2 py-2 mb-2">
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${col.color}`} />
                <h3 className="font-semibold text-sm">{col.title}</h3>
                <Badge variant="outline" className="text-[10px] h-4 px-1.5">{(tickets as any)[col.key].length}</Badge>
              </div>
              <Button variant="ghost" size="icon" className="w-7 h-7"><Plus className="w-3.5 h-3.5" /></Button>
            </div>
            <div className="space-y-2">
              {(tickets as any)[col.key].map((t: any) => (
                <Card key={t.id} className="p-3.5 hover:shadow-md transition-all cursor-pointer hover:-translate-y-0.5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-mono text-muted-foreground">{t.id}</span>
                    <MoreHorizontal className="w-3.5 h-3.5 text-muted-foreground" />
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
