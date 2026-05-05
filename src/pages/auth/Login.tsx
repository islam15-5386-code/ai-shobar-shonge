import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Sparkles } from "lucide-react";

export const AuthShell = ({ title, subtitle, children, footer }: any) => (
  <div className="min-h-screen grid lg:grid-cols-2">
    <div className="hidden lg:flex relative gradient-hero p-12 flex-col justify-between text-white overflow-hidden">
      <div className="absolute top-20 -right-20 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-float" />
      <Link to="/" className="flex items-center gap-2 relative">
        <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center">
          <Sparkles className="w-5 h-5" />
        </div>
        <span className="font-bold text-xl">SahajAI</span>
      </Link>
      <div className="relative">
        <h2 className="text-4xl font-bold leading-tight mb-4">"AI আমাদের সব ক্রেতাদের সাথে কথা বলে — দিন রাত।"</h2>
        <p className="text-white/80">— Rashed Hossain, Founder of Trendy BD</p>
      </div>
      <div className="text-xs text-white/60 relative">© 2026 SahajAI · Bangladesh</div>
    </div>
    <div className="flex items-center justify-center p-6 md:p-12 bg-background">
      <div className="w-full max-w-md animate-fade-in-up">
        <Link to="/" className="lg:hidden flex items-center gap-2 mb-8">
          <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center"><Sparkles className="w-5 h-5 text-white" /></div>
          <span className="font-bold text-lg">SahajAI</span>
        </Link>
        <h1 className="text-3xl font-bold mb-2">{title}</h1>
        <p className="text-muted-foreground mb-8">{subtitle}</p>
        {children}
        {footer && <div className="mt-6 text-center text-sm text-muted-foreground">{footer}</div>}
      </div>
    </div>
  </div>
);

export default function Login() {
  const nav = useNavigate();
  return (
    <AuthShell
      title="Welcome back"
      subtitle="Log in to your SahajAI dashboard"
      footer={<>Don't have an account? <Link to="/register" className="text-primary font-medium hover:underline">Sign up</Link></>}
    >
      <form onSubmit={(e) => { e.preventDefault(); nav("/dashboard"); }} className="space-y-4">
        <div className="space-y-2">
          <Label>Email</Label>
          <Input type="email" placeholder="you@business.com" defaultValue="demo@sahaj.ai" required />
        </div>
        <div className="space-y-2">
          <div className="flex justify-between">
            <Label>Password</Label>
            <Link to="/forgot-password" className="text-xs text-primary hover:underline">Forgot password?</Link>
          </div>
          <Input type="password" placeholder="••••••••" defaultValue="demo1234" required />
        </div>
        <Button type="submit" className="w-full gradient-primary border-0 shadow-glow h-11">Log in to Dashboard</Button>
        <Button type="button" variant="outline" className="w-full h-11">Continue with Google</Button>
      </form>
    </AuthShell>
  );
}
