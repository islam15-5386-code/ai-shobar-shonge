import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Sparkles, MessageSquare, Bot, Users, Zap, Shield, Check, ArrowRight, Globe, BarChart3, Headphones } from "lucide-react";

const features = [
  { icon: Bot, title: "Bangla AI Auto-Reply", desc: "বাংলায় সঠিক উত্তর দেয় আপনার ক্রেতাদের, ২৪/৭।" },
  { icon: MessageSquare, title: "Messenger + WhatsApp", desc: "Connect all your channels in one unified inbox." },
  { icon: Users, title: "Human Handover", desc: "Smart escalation when AI confidence drops." },
  { icon: Headphones, title: "Ticket Management", desc: "Kanban board, priority tags, agent assignment." },
  { icon: BarChart3, title: "Sentiment Insights", desc: "Real-time customer mood tracking and analytics." },
  { icon: Shield, title: "Bangladesh-First", desc: "bKash, Nagad, local delivery context built-in." },
];

const plans = [
  { name: "Starter", price: "৳1,499", period: "/month", desc: "For small Facebook pages", features: ["1,000 conversations/mo", "Messenger integration", "Basic AI replies", "Email support"], cta: "Start Free Trial", popular: false },
  { name: "Pro", price: "৳4,999", period: "/month", desc: "For growing online shops", features: ["15,000 conversations/mo", "All channels (FB, WA, Web)", "Bangla + English AI", "Ticket management", "Priority support"], cta: "Start Free Trial", popular: true },
  { name: "Business", price: "৳14,999", period: "/month", desc: "For clinics & coaching centers", features: ["Unlimited conversations", "Custom AI training", "Multiple agents", "API access", "Dedicated manager"], cta: "Book Demo", popular: false },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <header className="sticky top-0 z-50 glass border-b">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center shadow-glow">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg">SahajAI</span>
          </Link>
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
            <a href="#features" className="hover:text-foreground transition">Features</a>
            <a href="#pricing" className="hover:text-foreground transition">Pricing</a>
            <a href="#about" className="hover:text-foreground transition">About</a>
          </nav>
          <div className="flex items-center gap-2">
            <Link to="/login"><Button variant="ghost" size="sm">Log in</Button></Link>
            <Link to="/register"><Button size="sm" className="gradient-primary border-0 shadow-glow">Get Started</Button></Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden gradient-soft pt-20 pb-32">
        <div className="absolute top-20 -left-32 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-10 -right-32 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-float" style={{ animationDelay: "2s" }} />
        <div className="container mx-auto px-4 relative">
          <div className="max-w-4xl mx-auto text-center animate-fade-in-up">
            <Badge variant="outline" className="mb-6 px-4 py-1.5 bg-card border-primary/20">
              <Sparkles className="w-3 h-3 mr-2 text-primary" />
              Built for Bangladeshi businesses
            </Badge>
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-[1.05] mb-6">
              AI Customer Support for{" "}
              <span className="text-gradient">Bangladeshi Businesses</span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 font-bangla">
              বাংলা auto-reply, Messenger ও WhatsApp support, ticket management এবং human handover — সব এক জায়গায়।
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <Link to="/register">
                <Button size="lg" className="gradient-primary border-0 shadow-glow text-base h-12 px-7">
                  Start Free Trial <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="text-base h-12 px-7">
                Book a Demo
              </Button>
            </div>
            <div className="mt-10 flex items-center justify-center gap-6 text-xs text-muted-foreground">
              <div className="flex items-center gap-1.5"><Check className="w-4 h-4 text-success" /> 14-day free trial</div>
              <div className="flex items-center gap-1.5"><Check className="w-4 h-4 text-success" /> No credit card</div>
              <div className="flex items-center gap-1.5"><Check className="w-4 h-4 text-success" /> Cancel anytime</div>
            </div>
          </div>

          {/* Hero Mockup */}
          <div className="mt-16 max-w-5xl mx-auto animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
            <Card className="overflow-hidden shadow-elegant border-0 bg-card">
              <div className="h-10 bg-muted flex items-center gap-2 px-4 border-b">
                <div className="w-3 h-3 rounded-full bg-destructive/60" />
                <div className="w-3 h-3 rounded-full bg-warning/60" />
                <div className="w-3 h-3 rounded-full bg-success/60" />
              </div>
              <div className="grid md:grid-cols-3 gap-0">
                <div className="border-r p-5 bg-muted/30">
                  <div className="text-xs font-semibold text-muted-foreground mb-3">CONVERSATIONS</div>
                  {["Rahim", "Fatima", "Karim"].map((n, i) => (
                    <div key={i} className={`flex items-center gap-3 p-2 rounded-lg mb-1 ${i === 0 ? "bg-primary/10" : ""}`}>
                      <div className="w-8 h-8 rounded-full gradient-primary text-white text-xs flex items-center justify-center font-semibold">{n[0]}</div>
                      <div className="text-sm font-medium">{n}</div>
                    </div>
                  ))}
                </div>
                <div className="md:col-span-2 p-6 space-y-3 bg-gradient-to-br from-background to-muted/20">
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-2xl rounded-tl-sm px-4 py-2.5 max-w-xs text-sm font-bangla">ভাই, এই শাড়িটা কি স্টকে আছে?</div>
                  </div>
                  <div className="flex justify-end">
                    <div className="gradient-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-xs text-sm font-bangla">জ্বি, লাল, নীল, সবুজ রঙে আছে। দাম ২৪০০ টাকা।</div>
                  </div>
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-2xl rounded-tl-sm px-4 py-2.5 max-w-xs text-sm font-bangla">ডেলিভারি চার্জ কত?</div>
                  </div>
                  <Badge variant="outline" className="bg-success/10 text-success border-success/20"><Bot className="w-3 h-3 mr-1" /> AI replying...</Badge>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 container mx-auto px-4">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <Badge variant="outline" className="mb-4">Features</Badge>
          <h2 className="text-4xl md:text-5xl font-bold mb-4">Everything you need to <span className="text-gradient">delight customers</span></h2>
          <p className="text-muted-foreground">Built specifically for online shops, coaching centers, clinics, and service businesses in Bangladesh.</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <Card key={i} className="p-7 hover:shadow-elegant transition-all hover:-translate-y-1 group border bg-card">
              <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <f.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-sm text-muted-foreground">{f.desc}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <Badge variant="outline" className="mb-4">Pricing</Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Simple, transparent <span className="text-gradient">pricing</span></h2>
            <p className="text-muted-foreground">Pay in BDT. No hidden fees. Cancel anytime.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {plans.map((p) => (
              <Card key={p.name} className={`p-8 relative ${p.popular ? "ring-2 ring-primary shadow-elegant scale-105 border-0" : ""}`}>
                {p.popular && <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 gradient-primary border-0">Most Popular</Badge>}
                <h3 className="font-bold text-xl mb-1">{p.name}</h3>
                <p className="text-sm text-muted-foreground mb-5">{p.desc}</p>
                <div className="mb-6">
                  <span className="text-4xl font-extrabold">{p.price}</span>
                  <span className="text-muted-foreground">{p.period}</span>
                </div>
                <ul className="space-y-3 mb-8 text-sm">
                  {p.features.map((feat) => (
                    <li key={feat} className="flex items-start gap-2">
                      <Check className="w-4 h-4 text-success flex-shrink-0 mt-0.5" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
                <Link to="/register">
                  <Button className={`w-full ${p.popular ? "gradient-primary border-0 shadow-glow" : ""}`} variant={p.popular ? "default" : "outline"}>
                    {p.cta}
                  </Button>
                </Link>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 container mx-auto px-4">
        <Card className="gradient-hero p-12 md:p-16 text-center border-0 shadow-elegant overflow-hidden relative">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
          <div className="relative">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">Ready to transform your support?</h2>
            <p className="text-white/90 max-w-xl mx-auto mb-8">Join 500+ Bangladeshi businesses using SahajAI to delight customers 24/7.</p>
            <div className="flex flex-wrap justify-center gap-3">
              <Link to="/register"><Button size="lg" className="bg-white text-primary hover:bg-white/90 h-12 px-7">Start Free Trial</Button></Link>
              <Button size="lg" variant="outline" className="bg-transparent text-white border-white/40 hover:bg-white/10 h-12 px-7">Book Demo</Button>
            </div>
          </div>
        </Card>
      </section>

      <footer className="border-t py-10 bg-muted/30">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          © 2026 SahajAI. Made with ❤️ in Dhaka, Bangladesh.
        </div>
      </footer>
    </div>
  );
}
