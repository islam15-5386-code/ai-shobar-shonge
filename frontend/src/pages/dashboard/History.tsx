import { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";
import { Search, Download, Bot } from "lucide-react";
import { toast } from "sonner";

type ConversationMessage = {
  id: number;
  role: string;
  text: string;
  created_at: string;
};

type ConversationItem = {
  id: number;
  visitor_id: string;
  needs_human: boolean;
  updated_at: string;
  messages: ConversationMessage[];
};

type HistoryRow = {
  id: number;
  customer: string;
  avatar: string;
  message: string;
  channel: string;
  sentiment: "positive" | "neutral" | "negative";
  resolvedBy: "AI" | "Human";
  updatedAt: string;
};

const sentimentClass = (s: string) =>
  s === "positive"
    ? "bg-success/10 text-success border-success/20"
    : s === "negative"
      ? "bg-destructive/10 text-destructive border-destructive/20"
      : "";

const guessChannel = (visitorId: string) => {
  if (visitorId.startsWith("fb:")) return "Messenger";
  if (visitorId.startsWith("wa:")) return "WhatsApp";
  if (visitorId.startsWith("web:")) return "Website";
  return "Website";
};

const toCustomerName = (visitorId: string) => {
  const raw = visitorId.split(":").slice(1).join(":") || visitorId;
  return raw
    .replace(/[._-]+/g, " ")
    .replace(/\b\w/g, (m) => m.toUpperCase())
    .slice(0, 40);
};

const relativeTime = (iso: string) => {
  const diffMs = Date.now() - new Date(iso).getTime();
  const min = Math.floor(diffMs / 60000);
  if (min < 1) return "just now";
  if (min < 60) return `${min}m ago`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}h ago`;
  const day = Math.floor(hr / 24);
  return `${day}d ago`;
};

export default function History() {
  const [rows, setRows] = useState<HistoryRow[]>([]);
  const [q, setQ] = useState("");
  const [channel, setChannel] = useState("all");
  const [sentiment, setSentiment] = useState("all");

  const loadHistory = async () => {
    try {
      const data = await apiFetch<ConversationItem[]>("/api/conversations/history/");
      const mapped: HistoryRow[] = (data || []).map((c) => {
        const last = [...(c.messages || [])].sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
        )[0];
        const customer = toCustomerName(c.visitor_id);
        const sentimentGuess: "positive" | "neutral" | "negative" = c.needs_human ? "negative" : "neutral";
        return {
          id: c.id,
          customer,
          avatar: customer
            .split(" ")
            .slice(0, 2)
            .map((x) => x[0] || "")
            .join("")
            .toUpperCase(),
          message: last?.text || "No messages yet",
          channel: guessChannel(c.visitor_id),
          sentiment: sentimentGuess,
          resolvedBy: c.needs_human ? "Human" : "AI",
          updatedAt: c.updated_at,
        };
      });
      setRows(mapped);
    } catch {
      toast.error("History load failed. Please login first.");
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const filtered = useMemo(() => {
    return rows.filter((r) => {
      const qq = q.trim().toLowerCase();
      const okQ = !qq || r.customer.toLowerCase().includes(qq) || r.message.toLowerCase().includes(qq);
      const okC = channel === "all" || r.channel.toLowerCase() === channel;
      const okS = sentiment === "all" || r.sentiment === sentiment;
      return okQ && okC && okS;
    });
  }, [rows, q, channel, sentiment]);

  const exportCsv = () => {
    if (!filtered.length) {
      toast.error("No history to export");
      return;
    }
    const csvRows = [
      ["Conversation ID", "Customer", "Last Message", "Channel", "Sentiment", "Resolved By", "Updated At"],
      ...filtered.map((r) => [String(r.id), r.customer, r.message, r.channel, r.sentiment, r.resolvedBy, r.updatedAt]),
    ];
    const csv = csvRows.map((row) => row.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `conversation-history-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("CSV exported");
  };

  return (
    <div className="p-4 md:p-8">
      <PageHeader
        title="Conversation History"
        subtitle="Search and export past conversations"
        actions={
          <Button variant="outline" onClick={exportCsv}>
            <Download className="w-4 h-4 mr-1" /> Export CSV
          </Button>
        }
      />

      <Card className="p-4 mb-4 flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input placeholder="Search by customer name..." className="pl-9 bg-muted/50 border-0" value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
        <Select value={channel} onValueChange={setChannel}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Channel" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All channels</SelectItem>
            <SelectItem value="messenger">Messenger</SelectItem>
            <SelectItem value="whatsapp">WhatsApp</SelectItem>
            <SelectItem value="website">Website</SelectItem>
          </SelectContent>
        </Select>
        <Select value={sentiment} onValueChange={setSentiment}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Sentiment" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All sentiments</SelectItem>
            <SelectItem value="positive">Positive</SelectItem>
            <SelectItem value="neutral">Neutral</SelectItem>
            <SelectItem value="negative">Negative</SelectItem>
          </SelectContent>
        </Select>
      </Card>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Customer</TableHead>
              <TableHead className="hidden md:table-cell">Last message</TableHead>
              <TableHead>Channel</TableHead>
              <TableHead className="hidden md:table-cell">Sentiment</TableHead>
              <TableHead className="hidden md:table-cell">Resolved by</TableHead>
              <TableHead>Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((r) => (
              <TableRow key={r.id} className="hover:bg-muted/30 cursor-pointer">
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Avatar className="w-7 h-7"><AvatarFallback className="text-[10px] gradient-primary text-white">{r.avatar || "CU"}</AvatarFallback></Avatar>
                    <span className="font-medium text-sm">{r.customer}</span>
                  </div>
                </TableCell>
                <TableCell className="hidden md:table-cell text-sm text-muted-foreground truncate max-w-xs font-bangla">{r.message}</TableCell>
                <TableCell><Badge variant="outline">{r.channel}</Badge></TableCell>
                <TableCell className="hidden md:table-cell"><Badge variant="outline" className={sentimentClass(r.sentiment)}>{r.sentiment}</Badge></TableCell>
                <TableCell className="hidden md:table-cell">
                  <Badge variant="outline" className="bg-primary/5 border-primary/20">
                    <Bot className="w-3 h-3 mr-1" /> {r.resolvedBy}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs text-muted-foreground">{relativeTime(r.updatedAt)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
