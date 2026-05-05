import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { conversations } from "@/lib/mockData";
import { Search, Download, Bot } from "lucide-react";

const all = [...conversations, ...conversations.map((c) => ({ ...c, id: c.id + "x", time: "1d" }))];

export default function History() {
  return (
    <div className="p-4 md:p-8">
      <PageHeader title="Conversation History" subtitle="Search and export past conversations" actions={<Button variant="outline"><Download className="w-4 h-4 mr-1" /> Export CSV</Button>} />

      <Card className="p-4 mb-4 flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input placeholder="Search by customer name..." className="pl-9 bg-muted/50 border-0" />
        </div>
        <Select defaultValue="all"><SelectTrigger className="w-40"><SelectValue placeholder="Channel" /></SelectTrigger><SelectContent>
          <SelectItem value="all">All channels</SelectItem>
          <SelectItem value="messenger">Messenger</SelectItem>
          <SelectItem value="whatsapp">WhatsApp</SelectItem>
          <SelectItem value="web">Website</SelectItem>
        </SelectContent></Select>
        <Select defaultValue="all"><SelectTrigger className="w-40"><SelectValue placeholder="Sentiment" /></SelectTrigger><SelectContent>
          <SelectItem value="all">All sentiments</SelectItem>
          <SelectItem value="positive">Positive</SelectItem>
          <SelectItem value="neutral">Neutral</SelectItem>
          <SelectItem value="negative">Negative</SelectItem>
        </SelectContent></Select>
      </Card>

      <Card>
        <Table>
          <TableHeader><TableRow>
            <TableHead>Customer</TableHead>
            <TableHead className="hidden md:table-cell">Last message</TableHead>
            <TableHead>Channel</TableHead>
            <TableHead className="hidden md:table-cell">Sentiment</TableHead>
            <TableHead className="hidden md:table-cell">Resolved by</TableHead>
            <TableHead>Time</TableHead>
          </TableRow></TableHeader>
          <TableBody>
            {all.map((c) => (
              <TableRow key={c.id} className="hover:bg-muted/30 cursor-pointer">
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Avatar className="w-7 h-7"><AvatarFallback className="text-[10px] gradient-primary text-white">{c.avatar}</AvatarFallback></Avatar>
                    <span className="font-medium text-sm">{c.name}</span>
                  </div>
                </TableCell>
                <TableCell className="hidden md:table-cell text-sm text-muted-foreground truncate max-w-xs font-bangla">{c.message}</TableCell>
                <TableCell><Badge variant="outline">{c.channel}</Badge></TableCell>
                <TableCell className="hidden md:table-cell">
                  <Badge variant="outline" className={c.sentiment === "positive" ? "bg-success/10 text-success border-success/20" : c.sentiment === "negative" ? "bg-destructive/10 text-destructive border-destructive/20" : ""}>{c.sentiment}</Badge>
                </TableCell>
                <TableCell className="hidden md:table-cell"><Badge variant="outline" className="bg-primary/5 border-primary/20"><Bot className="w-3 h-3 mr-1" /> AI</Badge></TableCell>
                <TableCell className="text-xs text-muted-foreground">{c.time} ago</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
