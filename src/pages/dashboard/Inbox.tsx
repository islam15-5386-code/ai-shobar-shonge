import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { conversations, messages } from "@/lib/mockData";
import { Search, Send, Paperclip, Smile, UserPlus, Ticket, CheckCircle2, Hand, Bot, Sparkles, Phone, Mail, MapPin } from "lucide-react";

export default function Inbox() {
  const [active, setActive] = useState(conversations[0]);

  const sentimentColor = (s: string) => s === "positive" ? "bg-success/10 text-success border-success/20" : s === "negative" ? "bg-destructive/10 text-destructive border-destructive/20" : "bg-muted text-muted-foreground";

  return (
    <div className="h-[calc(100vh-4rem)] grid lg:grid-cols-[320px_1fr_320px] grid-cols-1">
      {/* List */}
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
            <button key={c.id} onClick={() => setActive(c)} className={`w-full flex gap-3 p-4 border-b text-left hover:bg-muted/50 transition ${active.id === c.id ? "bg-primary/5 border-l-2 border-l-primary" : ""}`}>
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

      {/* Chat */}
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
            <Button size="sm" variant="outline"><Hand className="w-3.5 h-3.5 mr-1" /> Take Over</Button>
            <Button size="sm" variant="outline" className="hidden md:inline-flex"><UserPlus className="w-3.5 h-3.5 mr-1" /> Assign</Button>
            <Button size="sm" variant="outline" className="hidden md:inline-flex"><Ticket className="w-3.5 h-3.5 mr-1" /> Ticket</Button>
            <Button size="sm" className="gradient-primary border-0"><CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Resolve</Button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-6 space-y-3">
          {messages.map((m, i) => (
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
          <div className="flex items-center gap-2 bg-muted/50 rounded-xl px-3 py-2">
            <Button size="icon" variant="ghost" className="w-8 h-8"><Paperclip className="w-4 h-4" /></Button>
            <Input placeholder="Type your message... / use AI suggestions" className="border-0 bg-transparent focus-visible:ring-0" />
            <Button size="icon" variant="ghost" className="w-8 h-8"><Smile className="w-4 h-4" /></Button>
            <Button size="icon" className="gradient-primary border-0 w-9 h-9"><Send className="w-4 h-4" /></Button>
          </div>
        </div>
      </div>

      {/* Profile */}
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
          <div className="space-y-2 text-xs">
            <Card className="p-3"><div className="font-medium">Order #4521</div><div className="text-muted-foreground">৳3,200 · Delivered</div></Card>
            <Card className="p-3"><div className="font-medium">Order #4310</div><div className="text-muted-foreground">৳1,850 · Delivered</div></Card>
          </div>
        </div>
      </div>
    </div>
  );
}
