import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { stats, sentimentData, channelData, conversations } from "@/lib/mockData";
import { ArrowUpRight, MessagesSquare, Ticket, Bot, UserCheck, Clock, TrendingUp, Download } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, PieChart, Pie, Cell, Legend } from "recharts";

const kpis = [
  { label: "Total Conversations", value: stats.totalConversations.toLocaleString(), change: "+12.4%", icon: MessagesSquare, color: "from-violet-500 to-fuchsia-500" },
  { label: "Open Tickets", value: stats.openTickets, change: "-8%", icon: Ticket, color: "from-amber-500 to-orange-500" },
  { label: "AI Resolved", value: stats.aiResolved.toLocaleString(), change: "+18%", icon: Bot, color: "from-emerald-500 to-teal-500" },
  { label: "Human Handover", value: stats.humanHandover, change: "+3%", icon: UserCheck, color: "from-blue-500 to-cyan-500" },
];

export default function Overview() {
  const navigate = useNavigate();

  const handleExport = () => {
    const rows = [
      ["Metric", "Value"],
      ["Total Conversations", String(stats.totalConversations)],
      ["Open Tickets", String(stats.openTickets)],
      ["AI Resolved", String(stats.aiResolved)],
      ["Human Handover", String(stats.humanHandover)],
      ["Average Response Time", String(stats.avgResponseTime)],
      ["Resolution Rate", `${stats.resolutionRate}%`],
    ];
    const csv = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `supportbond-overview-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
  };

  const handleNewConversation = () => {
    navigate("/dashboard/inbox");
  };

  return (
    <div className="p-4 md:p-8">
      <PageHeader
        title="Dashboard"
        subtitle="Welcome, Rashed! Here's how your support is performing today."
        actions={
          <>
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="w-4 h-4 mr-1" /> Export
            </Button>
            <Button size="sm" className="gradient-primary border-0" onClick={handleNewConversation}>
              + New Conversation
            </Button>
          </>
        }
      />

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {kpis.map((k, i) => (
          <Card key={i} className="p-5 hover:shadow-elegant transition-all group cursor-pointer border bg-card relative overflow-hidden">
            <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${k.color} opacity-10 rounded-full blur-2xl`} />
            <div className="relative">
              <div className="flex items-start justify-between mb-3">
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${k.color} flex items-center justify-center shadow-md group-hover:scale-110 transition`}>
                  <k.icon className="w-5 h-5 text-white" />
                </div>
                <Badge variant="outline" className={`text-xs ${k.change.startsWith("+") ? "text-success border-success/30 bg-success/5" : "text-destructive border-destructive/30 bg-destructive/5"}`}>
                  {k.change} <ArrowUpRight className="w-3 h-3 ml-0.5" />
                </Badge>
              </div>
              <div className="text-2xl font-bold">{k.value}</div>
              <div className="text-xs text-muted-foreground mt-1">{k.label}</div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6 mb-6">
        <Card className="lg:col-span-2 p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-semibold">Customer Sentiment</h3>
              <p className="text-xs text-muted-foreground">Last 7 days</p>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <Badge variant="outline" className="bg-success/10 text-success border-success/20"><span className="w-2 h-2 rounded-full bg-success mr-1.5"/>Positive</Badge>
              <Badge variant="outline"><span className="w-2 h-2 rounded-full bg-muted-foreground mr-1.5"/>Neutral</Badge>
              <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive/20"><span className="w-2 h-2 rounded-full bg-destructive mr-1.5"/>Negative</Badge>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={sentimentData}>
              <defs>
                <linearGradient id="pos" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="hsl(145 65% 45%)" stopOpacity={0.4}/><stop offset="95%" stopColor="hsl(145 65% 45%)" stopOpacity={0}/></linearGradient>
                <linearGradient id="neu" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="hsl(220 10% 55%)" stopOpacity={0.3}/><stop offset="95%" stopColor="hsl(220 10% 55%)" stopOpacity={0}/></linearGradient>
                <linearGradient id="neg" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="hsl(0 78% 60%)" stopOpacity={0.3}/><stop offset="95%" stopColor="hsl(0 78% 60%)" stopOpacity={0}/></linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 12, boxShadow: "var(--shadow-lg)" }} />
              <Area type="monotone" dataKey="positive" stroke="hsl(145 65% 45%)" fill="url(#pos)" strokeWidth={2.5} />
              <Area type="monotone" dataKey="neutral" stroke="hsl(220 10% 55%)" fill="url(#neu)" strokeWidth={2} />
              <Area type="monotone" dataKey="negative" stroke="hsl(0 78% 60%)" fill="url(#neg)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-6">
          <h3 className="font-semibold mb-1">Channels</h3>
          <p className="text-xs text-muted-foreground mb-4">Conversation source</p>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={channelData} dataKey="value" innerRadius={50} outerRadius={80} paddingAngle={3}>
                {channelData.map((c, i) => <Cell key={i} fill={c.color} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2 mt-4">
            {channelData.map((c) => (
              <div key={c.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full" style={{ background: c.color }} />{c.name}</div>
                <span className="font-medium">{c.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Recent Conversations</h3>
            <Button variant="ghost" size="sm">View all</Button>
          </div>
          <div className="space-y-1">
            {conversations.slice(0, 5).map((c) => (
              <div key={c.id} className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted/50 transition cursor-pointer">
                <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center text-white text-sm font-semibold">{c.avatar}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <div className="font-medium text-sm">{c.name}</div>
                    <Badge variant="outline" className="text-[10px] h-4 px-1.5">{c.channel}</Badge>
                  </div>
                  <div className="text-sm text-muted-foreground truncate">{c.message}</div>
                </div>
                <div className="text-xs text-muted-foreground">{c.time}</div>
              </div>
            ))}
          </div>
        </Card>

        <div className="space-y-6">
          <Card className="p-6 gradient-primary text-white border-0 shadow-elegant">
            <Clock className="w-8 h-8 mb-3 opacity-90" />
            <div className="text-3xl font-bold">{stats.avgResponseTime}</div>
            <div className="text-sm opacity-90 mt-1">Avg. response time</div>
            <div className="text-xs opacity-75 mt-2">↓ 32% from last week</div>
          </Card>
          <Card className="p-6">
            <TrendingUp className="w-8 h-8 mb-3 text-success" />
            <div className="text-3xl font-bold">{stats.resolutionRate}%</div>
            <div className="text-sm text-muted-foreground mt-1">Resolution rate</div>
            <div className="h-2 bg-muted rounded-full mt-3 overflow-hidden">
              <div className="h-full gradient-primary" style={{ width: `${stats.resolutionRate}%` }} />
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

