import { NavLink, Outlet, useLocation } from "react-router-dom";
import { LayoutDashboard, MessagesSquare, Ticket, BookOpen, Package, Plug, Settings, History, CreditCard, Bell, Search, Bot, Sparkles } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "@/lib/api";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

const nav = [
  { to: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { to: "/dashboard/inbox", label: "Live Inbox", icon: MessagesSquare, badge: "12" },
  { to: "/dashboard/tickets", label: "Tickets", icon: Ticket, badge: "38" },
  { to: "/dashboard/faqs", label: "FAQ Knowledge", icon: BookOpen },
  { to: "/dashboard/products", label: "Products", icon: Package },
  { to: "/dashboard/history", label: "History", icon: History },
  { to: "/dashboard/integrations", label: "Integrations", icon: Plug },
  { to: "/dashboard/ai-settings", label: "AI Settings", icon: Bot },
  { to: "/dashboard/billing", label: "Billing", icon: CreditCard },
];

export const DashboardLayout = () => {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const [planName, setPlanName] = useState("Plan");
  const [used, setUsed] = useState(0);
  const [limit, setLimit] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, text: "New message এসেছে Live Inbox-এ", time: "2m ago", read: false },
    { id: 2, text: "Ticket #1024 pending আছে", time: "8m ago", read: false },
    { id: 3, text: "AI usage 80% cross করেছে", time: "15m ago", read: true },
  ]);

  const usagePct = useMemo(() => {
    if (!limit || limit <= 0) return 0;
    return Math.max(0, Math.min(100, Math.round((used / limit) * 100)));
  }, [used, limit]);

  const unreadCount = useMemo(() => notifications.filter((n) => !n.read).length, [notifications]);

  useEffect(() => {
    let mounted = true;
    let timer: number | undefined;

    const loadUsage = async () => {
      try {
        const [subRes, usageRes] = await Promise.allSettled([
          apiFetch<any>("/api/billing/subscription/"),
          apiFetch<any>("/api/billing/usage/?metric=messages"),
        ]);
        if (!mounted) return;
        const sub = subRes.status === "fulfilled" ? subRes.value : null;
        const usage = usageRes.status === "fulfilled" ? usageRes.value : null;
        setPlanName(sub?.plan?.name || "Plan");
        setUsed(Number(usage?.quantity || 0));
        setLimit(Number(usage?.limit || 0));
        setIsLoaded(true);
      } catch {
        if (!mounted) return;
        setIsLoaded(true);
      }
    };

    loadUsage();
    timer = window.setInterval(loadUsage, 10000);
    return () => {
      mounted = false;
      if (timer) window.clearInterval(timer);
    };
  }, []);

  return (
    <div className="min-h-screen flex w-full bg-[#f6f8fb] text-slate-900">
      {/* Sidebar */}
      <aside className={`${open ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0 fixed lg:sticky top-0 left-0 z-40 h-screen w-72 bg-sidebar text-sidebar-foreground flex flex-col transition-transform border-r border-sidebar-border`}>
        <div className="h-16 flex items-center gap-2 px-6 border-b border-sidebar-border bg-white">
          <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-slate-900 text-base leading-tight">Shobar Shonge</div>
            <div className="text-[10px] text-sidebar-foreground/70 uppercase tracking-wider">Customer Support</div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/dashboard"}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-md"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-slate-900"
                }`
              }
            >
              <item.icon className="w-4 h-4" />
              <span className="flex-1">{item.label}</span>
              {item.badge && <Badge className="bg-accent text-accent-foreground text-[10px] h-5 px-1.5">{item.badge}</Badge>}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-sidebar-border">
          <div className="bg-sidebar-accent rounded-xl p-4 border border-sidebar-border">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-primary" />
              <div className="text-xs font-semibold text-slate-900">{planName}</div>
            </div>
            <div className="text-[11px] text-sidebar-foreground/80 mb-3">
              {isLoaded ? `${used.toLocaleString()} / ${limit.toLocaleString()} conversations used` : "Loading usage..."}
            </div>
            <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full gradient-primary transition-all duration-500" style={{ width: `${usagePct}%` }} />
            </div>
          </div>
        </div>
      </aside>

      {open && <div onClick={() => setOpen(false)} className="fixed inset-0 bg-black/40 z-30 lg:hidden" />}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white/95 backdrop-blur-md border-b sticky top-0 z-20 flex items-center gap-3 px-4 lg:px-6">
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setOpen(!open)}>
            <LayoutDashboard className="w-5 h-5" />
          </Button>
          <div className="relative flex-1 max-w-md hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input placeholder="Search conversations, tickets, customers..." className="pl-9 bg-slate-100 border-slate-200" />
          </div>
          <div className="flex-1 md:hidden" />
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && <span className="absolute top-2 right-2 w-2 h-2 bg-destructive rounded-full" />}
              </Button>
            </PopoverTrigger>
            <PopoverContent align="end" className="w-80 p-0 overflow-hidden">
              <div className="px-4 py-3 border-b flex items-center justify-between">
                <div className="font-semibold text-sm">Notifications</div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() => setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))}
                >
                  Mark all read
                </Button>
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notifications.map((n) => (
                  <button
                    key={n.id}
                    onClick={() => setNotifications((prev) => prev.map((item) => (item.id === n.id ? { ...item, read: true } : item)))}
                    className={`w-full text-left px-4 py-3 border-b last:border-b-0 hover:bg-muted/50 ${n.read ? "opacity-70" : ""}`}
                  >
                    <div className="text-sm">{n.text}</div>
                    <div className="text-[11px] text-muted-foreground mt-1">{n.time}</div>
                  </button>
                ))}
              </div>
            </PopoverContent>
          </Popover>
          <NavLink to="/dashboard/onboarding" className="hidden sm:block">
            <Badge variant="outline" className="gap-1"><Sparkles className="w-3 h-3" /> Setup</Badge>
          </NavLink>
          <Avatar className="w-9 h-9 ring-2 ring-primary/20">
            <AvatarFallback className="gradient-primary text-white text-xs font-semibold">RH</AvatarFallback>
          </Avatar>
        </header>
        <main key={location.pathname} className="flex-1 animate-fade-in-up bg-[#f6f8fb]">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
