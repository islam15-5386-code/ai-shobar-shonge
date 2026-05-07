import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  ArrowUp,
  BadgeCheck,
  Bot,
  BookOpen,
  CircleCheckBig,
  CreditCard,
  Crown,
  Headphones,
  History,
  LayoutDashboard,
  Mail,
  MessageSquare,
  Package,
  Plug,
  Settings,
  Sparkles,
  Star,
  Ticket,
  Users,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const serviceFeatures = [
  {
    icon: Bot,
    title: "Bangla + English AI Reply",
    desc: "Auto-reply customers with better intent understanding and confidence-aware escalation.",
    route: "/dashboard/ai-settings",
    points: ["Auto reply toggle + confidence threshold", "Bangla/English tone control", "Escalation rules to human agents"],
  },
  {
    icon: MessageSquare,
    title: "Unified Live Inbox",
    desc: "Handle customer chats from one place and reduce missed conversation response time.",
    route: "/dashboard/inbox",
    points: ["Website, Messenger, WhatsApp conversations", "Take over, assign, resolve actions", "Per-customer chat context and timeline"],
  },
  {
    icon: Ticket,
    title: "Ticket Workflow",
    desc: "Create, assign, prioritize, and track tickets with status visibility for your whole team.",
    route: "/dashboard/tickets",
    points: ["Kanban-style status tracking", "Priority and assignment controls", "Auto ticket from AI escalation"],
  },
  {
    icon: BookOpen,
    title: "FAQ Knowledge Base",
    desc: "Store reusable answers so agents and AI can serve customers faster and more consistently.",
    route: "/dashboard/faqs",
    points: ["Add/edit/delete FAQ entries", "Category + language-based organization", "Bulk import and AI re-index support"],
  },
  {
    icon: Plug,
    title: "Integrations",
    desc: "Connect tools and channels with minimal setup to keep operations centralized.",
    route: "/dashboard/integrations",
    points: ["Website widget configuration", "Messenger/WhatsApp webhook setup", "Channel status and credentials overview"],
  },
  {
    icon: History,
    title: "Action History",
    desc: "Review team activity and support events to improve quality and accountability.",
    route: "/dashboard/history",
    points: ["Conversation history records", "Search and channel filters", "CSV export for reporting"],
  },
  {
    icon: CreditCard,
    title: "Billing Control",
    desc: "Manage plans and usage clearly with one billing section in your dashboard.",
    route: "/dashboard/billing",
    points: ["Plan comparison and current plan", "Usage meter and limits", "Sandbox payment checkout flow"],
  },
  {
    icon: Settings,
    title: "AI Settings",
    desc: "Tune behavior, tone, and automation rules to match your service process.",
    route: "/dashboard/ai-settings",
    points: ["System prompt and reply style", "Confidence-based handover", "Refund/negative sentiment rules"],
  },
];

const systemModules = [
  { title: "Overview Dashboard", icon: LayoutDashboard, desc: "KPIs, stats, and system health in one summary screen.", points: ["Conversation + ticket totals", "AI performance snapshot", "Usage and plan visibility"] },
  { title: "Live Inbox", icon: MessageSquare, desc: "Real-time incoming conversations and response handling.", points: ["Website/Messenger/WhatsApp chats", "Take over / assign / resolve", "Customer context panel"] },
  { title: "Tickets", icon: Ticket, desc: "Issue management with priority and progress tracking.", points: ["Kanban ticket pipeline", "Priority + owner assignment", "Human handover support"] },
  { title: "FAQ Knowledge", icon: BookOpen, desc: "Central library of support answers and reusable content.", points: ["Create/update/delete FAQ", "Category + language control", "Re-index for AI"] },
  { title: "Products", icon: Package, desc: "Product/service references used inside support workflows.", points: ["Vendor/business product catalog", "Stock, price, policy fields", "AI product-aware replies"] },
  { title: "Integrations", icon: Plug, desc: "Connect external platforms and enable channel sync.", points: ["Widget setup keys", "Messenger webhook config", "WhatsApp Cloud API config"] },
  { title: "AI Settings", icon: Bot, desc: "Configure intelligence and AI-driven automation behavior.", points: ["Auto-reply switch", "Confidence threshold", "Escalation rules"] },
  { title: "History", icon: History, desc: "Audit activity log for actions and operational events.", points: ["Conversation history table", "Filter by channel/sentiment", "CSV export"] },
  { title: "Billing", icon: CreditCard, desc: "Manage plan, payment, and usage from one place.", points: ["Current subscription", "Usage meters", "Sandbox checkout flow"] },
  { title: "Onboarding", icon: Sparkles, desc: "Step-by-step initial setup for fast team activation.", points: ["Business setup", "Category selection", "Starter config"] },
  { title: "Login", icon: Headphones, desc: "Secure access point for team members.", points: ["JWT-based authentication", "Role-based access", "Session start"] },
  { title: "Register", icon: Users, desc: "Create a new account and start onboarding.", points: ["Create user + business", "Owner role bootstrap", "Start setup flow"] },
];

const testimonials = [
  { name: "Rafiul Islam", role: "Support Manager", quote: "Shobar Shonge gave our team one clear support flow instead of scattered tools." },
  { name: "Nusrat Jahan", role: "Operations Lead", quote: "The inbox and ticket workflow significantly improved our response consistency." },
  { name: "Sabbir Ahmed", role: "Founder", quote: "The AI settings and FAQ base made support faster without losing answer quality." },
];

function initials(name: string) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

export default function Landing() {
  const year = useMemo(() => new Date().getFullYear(), []);

  return (
    <div className="min-h-screen bg-[#f6f8fb] text-slate-900">
      <div className="h-9 bg-[#1f2127] text-white text-sm flex items-center justify-between px-4 md:px-8">
        <span className="font-medium">Shobar Shonge | AI-Powered Customer Service Platform</span>
        <Link to="/register">
          <Button size="sm" className="h-7 bg-[#78c043] hover:bg-[#65a938] text-black font-semibold">Start now</Button>
        </Link>
      </div>

      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 md:px-6 h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <span className="h-8 w-8 rounded-md bg-[#933f67] text-white grid place-items-center"><BadgeCheck className="w-4 h-4" /></span>
            <span className="text-3xl font-black tracking-tight">Shobar Shonge</span>
          </Link>
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
            <a href="#home" className="hover:text-[#933f67]">Home</a>
            <a href="#features" className="hover:text-[#933f67]">Services</a>
            <a href="#system" className="hover:text-[#933f67]">Full System</a>
            <a href="#reviews" className="hover:text-[#933f67]">Reviews</a>
          </nav>
          <div className="flex items-center gap-2">
            <Link to="/login"><Button variant="outline" className="hidden md:inline-flex">Log in</Button></Link>
            <Link to="/dashboard"><Button className="bg-[#933f67] hover:bg-[#7d3156]">Open Dashboard</Button></Link>
          </div>
        </div>
      </header>

      <section id="home" className="relative overflow-hidden bg-gradient-to-r from-[#f4e9f0] to-[#f8f2f6]">
        <div className="max-w-6xl mx-auto px-4 md:px-6 py-20 grid lg:grid-cols-2 gap-10 items-center">
          <div>
            <Badge className="bg-white text-slate-700 hover:bg-white mb-5">Built for modern customer support teams</Badge>
            <h1 className="text-4xl md:text-6xl font-black leading-tight">All Your Customer Support Operations in One Platform</h1>
            <p className="mt-5 text-slate-600 max-w-xl">
              Shobar Shonge combines AI reply, live inbox, tickets, FAQs, integrations, billing, and analytics so
              your team can deliver faster support with better consistency.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/register"><Button className="bg-[#933f67] hover:bg-[#7d3156]">Create Account</Button></Link>
              <Link to="/dashboard"><Button variant="outline">Explore Full System</Button></Link>
            </div>
            <div className="mt-10 grid sm:grid-cols-3 gap-3 max-w-2xl">
              {[
                "9 Core Modules",
                "Real-time Inbox + Tickets",
                "AI + Human Handover",
              ].map((item) => (
                <Card key={item} className="p-4 bg-white/80 backdrop-blur border-slate-200 shadow-sm text-center font-semibold">
                  {item}
                </Card>
              ))}
            </div>
          </div>

          <Card className="p-3 bg-white/90 border-slate-200 shadow-xl rotate-[-4deg] lg:translate-x-6 overflow-hidden">
            <img
              src="/supportbond-preview.svg"
              alt="SupportBond AI dashboard preview"
              className="w-full h-auto rounded-md"
              loading="lazy"
            />
          </Card>
        </div>
      </section>

      <section id="features" className="py-20">
        <div className="max-w-6xl mx-auto px-4 md:px-6">
          <div className="text-center mb-10">
            <h2 className="text-4xl font-black">Our Services</h2>
            <p className="text-slate-600 mt-3">Everything needed to run your complete customer support workflow.</p>
          </div>
          <div className="relative mb-5 rounded-2xl border border-slate-200 bg-gradient-to-r from-[#fff7fb] via-[#f9fbff] to-[#f4f8ff] p-4 md:p-5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <div className="text-sm font-semibold text-[#933f67]">Tab Guide</div>
                <div className="text-sm text-slate-600">Each card explains what that dashboard tab does and lets you open it instantly.</div>
              </div>
              <div className="text-xs text-slate-500">Detailed module coverage for onboarding and demos</div>
            </div>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {serviceFeatures.map((feature) => (
              <Card
                key={feature.title}
                className="group p-5 border-slate-200 bg-white hover:border-[#d9b4c8] hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
              >
                <div className="w-10 h-10 rounded-md bg-slate-950 text-white grid place-items-center mb-4 group-hover:bg-[#933f67] transition-colors">
                  <feature.icon className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-lg mb-2 leading-tight">{feature.title}</h3>
                <p className="text-sm text-slate-600">{feature.desc}</p>
                <div className="mt-4 pt-3 border-t border-slate-100 space-y-1.5">
                  {feature.points.map((point) => (
                    <div key={point} className="text-xs text-slate-700 flex items-start gap-1.5">
                      <span className="mt-1 inline-block h-1.5 w-1.5 rounded-full bg-[#933f67]" />
                      <span>{point}</span>
                    </div>
                  ))}
                </div>
                <Link
                  to={feature.route}
                  className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-[#933f67] hover:text-[#7d3156]"
                >
                  Open Tab <ArrowRight className="w-4 h-4" />
                </Link>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section id="system" className="py-20 bg-white border-y border-slate-200">
        <div className="max-w-6xl mx-auto px-4 md:px-6">
          <div className="text-center mb-10">
            <div className="text-6xl font-black text-[#933f67]">Full System</div>
            <h2 className="text-4xl font-black">All Functional Modules Are Live</h2>
            <p className="text-slate-600 mt-3">Demo preview only. Login is required to access real modules.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {systemModules.map((module) => (
              <Card key={module.title} className="p-5 border-slate-200 bg-[#fbfcff]">
                <div className="flex items-start justify-between gap-2">
                  <div className="w-10 h-10 rounded-md bg-slate-900 text-white grid place-items-center">
                    <module.icon className="w-5 h-5" />
                  </div>
                  <Badge variant="outline" className="text-xs">Demo Screenshot</Badge>
                </div>
                <h3 className="font-semibold text-lg mt-4">{module.title}</h3>
                <p className="text-slate-600 text-sm mt-2">{module.desc}</p>
                <div className="mt-3 space-y-1.5">
                  {module.points.map((point) => (
                    <div key={point} className="text-xs text-slate-700 flex items-start gap-1.5">
                      <span className="mt-1 inline-block h-1.5 w-1.5 rounded-full bg-[#933f67]" />
                      <span>{point}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-4 rounded-md border border-slate-200 bg-white p-2">
                  <img src="/supportbond-preview.svg" alt={`${module.title} demo screenshot`} className="w-full rounded" loading="lazy" />
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section id="reviews" className="py-20">
        <div className="max-w-6xl mx-auto px-4 md:px-6">
          <div className="text-center mb-10">
            <h2 className="text-4xl font-black">Trusted by Teams</h2>
            <p className="text-slate-600 mt-3">Real feedback from people managing daily customer operations.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-4">
            {testimonials.map((item) => (
              <Card key={item.name} className="p-5 bg-white border-slate-200">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-[#78c043] text-slate-900 grid place-items-center font-bold">
                    {initials(item.name)}
                  </div>
                  <p className="text-slate-600">{item.quote}</p>
                </div>
                <div className="mt-4">
                  <div className="font-bold">{item.name}</div>
                  <div className="text-sm text-slate-500">{item.role}</div>
                  <div className="mt-2 flex gap-1 text-amber-500">{Array.from({ length: 5 }).map((_, i) => <Star key={i} className="w-4 h-4 fill-current" />)}</div>
                </div>
              </Card>
            ))}
          </div>

          <Card className="mt-12 p-7 md:p-10 bg-[#050a1e] text-white border-0">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <h3 className="text-4xl font-black">Run Your Full Support System with Shobar Shonge</h3>
                <p className="text-white/75 mt-2">From onboarding to AI setup, inbox to tickets, everything is connected.</p>
              </div>
              <div className="flex gap-2">
                <Link to="/register"><Button className="bg-[#933f67] hover:bg-[#7d3156]">Start Free</Button></Link>
                <Link to="/dashboard"><Button variant="outline" className="border-white/40 text-white hover:bg-white/10">Go to Dashboard</Button></Link>
              </div>
            </div>
          </Card>
        </div>
      </section>

      <footer className="bg-[#020816] text-white pt-12 pb-6">
        <div className="max-w-6xl mx-auto px-4 md:px-6">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="h-8 w-8 rounded-md bg-[#933f67] text-white grid place-items-center"><BadgeCheck className="w-4 h-4" /></span>
                <span className="text-3xl font-black">Shobar Shonge</span>
              </div>
              <p className="text-white/75">AI-powered customer service platform with a complete operational dashboard system.</p>
            </div>
            <div>
              <h4 className="font-bold mb-3">Quick Access</h4>
              <ul className="space-y-2 text-white/80">
                <li><Link to="/dashboard" className="hover:text-white">Dashboard</Link></li>
                <li><Link to="/dashboard/onboarding" className="hover:text-white">Onboarding</Link></li>
                <li><Link to="/dashboard/ai-settings" className="hover:text-white">AI Settings</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-3">Fast Actions</h4>
              <div className="flex gap-2">
                <Link to="/dashboard/inbox"><Button size="sm" variant="outline" className="text-white border-white/30">Inbox</Button></Link>
                <Link to="/dashboard/tickets"><Button size="sm" variant="outline" className="text-white border-white/30">Tickets</Button></Link>
                <Link to="/dashboard/billing"><Button size="sm" variant="outline" className="text-white border-white/30">Billing</Button></Link>
              </div>
            </div>
          </div>

          <div className="pt-5 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-2 text-sm text-white/70">
            <span>Copyright {year} Shobar Shonge, All Rights Reserved</span>
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
              className="inline-flex items-center gap-1 hover:text-white"
            >
              <ArrowUp className="w-4 h-4" /> Back to top
            </button>
          </div>
        </div>
      </footer>

      <div className="fixed bottom-5 right-5 flex flex-col gap-2 z-50">
        <Link to="/dashboard/inbox" className="w-12 h-12 rounded-full bg-[#22c55e] text-white grid place-items-center shadow-lg">
          <MessageSquare className="w-5 h-5" />
        </Link>
        <Link to="/dashboard/tickets" className="w-12 h-12 rounded-full bg-slate-950 text-white grid place-items-center shadow-lg">
          <CircleCheckBig className="w-5 h-5" />
        </Link>
        <Link to="/dashboard/ai-settings" className="w-12 h-12 rounded-full bg-[#933f67] text-white grid place-items-center shadow-lg">
          <Crown className="w-5 h-5" />
        </Link>
      </div>

      <div className="fixed bottom-5 left-5 z-50">
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="w-10 h-10 rounded-full bg-slate-950 text-white grid place-items-center shadow-lg"
          aria-label="Back to top"
        >
          <ArrowUp className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
