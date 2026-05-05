import { NavLink, Outlet, useLocation } from "react-router-dom";
import { LayoutDashboard, MessagesSquare, Ticket, BookOpen, Package, Plug, Settings, History, CreditCard, Bell, Search, Bot, Sparkles } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useState } from "react";

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

  return (
    <div className="min-h-screen flex w-full bg-muted/30">
      {/* Sidebar */}
      <aside className={`${open ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0 fixed lg:sticky top-0 left-0 z-40 h-screen w-64 bg-sidebar text-sidebar-foreground flex flex-col transition-transform`}>
        <div className="h-16 flex items-center gap-2 px-6 border-b border-sidebar-border">
          <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center shadow-glow">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-white text-base leading-tight">SahajAI</div>
            <div className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider">Customer Support</div>
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
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-white"
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
          <div className="bg-sidebar-accent rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-accent" />
              <div className="text-xs font-semibold text-white">Pro Plan</div>
            </div>
            <div className="text-[11px] text-sidebar-foreground/70 mb-3">9,421 / 15,000 conversations used</div>
            <div className="h-1.5 bg-sidebar-border rounded-full overflow-hidden">
              <div className="h-full gradient-primary" style={{ width: "63%" }} />
            </div>
          </div>
        </div>
      </aside>

      {open && <div onClick={() => setOpen(false)} className="fixed inset-0 bg-black/40 z-30 lg:hidden" />}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-card/80 backdrop-blur-md border-b sticky top-0 z-20 flex items-center gap-3 px-4 lg:px-6">
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setOpen(!open)}>
            <LayoutDashboard className="w-5 h-5" />
          </Button>
          <div className="relative flex-1 max-w-md hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input placeholder="Search conversations, tickets, customers..." className="pl-9 bg-muted/50 border-0" />
          </div>
          <div className="flex-1 md:hidden" />
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="w-5 h-5" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-destructive rounded-full" />
          </Button>
          <NavLink to="/dashboard/onboarding" className="hidden sm:block">
            <Badge variant="outline" className="gap-1"><Sparkles className="w-3 h-3" /> Setup</Badge>
          </NavLink>
          <Avatar className="w-9 h-9 ring-2 ring-primary/20">
            <AvatarFallback className="gradient-primary text-white text-xs font-semibold">RH</AvatarFallback>
          </Avatar>
        </header>
        <main key={location.pathname} className="flex-1 animate-fade-in-up">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
