import { Link, useNavigate } from "react-router-dom";
<<<<<<< HEAD
import { useEffect, useState } from "react";
=======
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Sparkles } from "lucide-react";
import { apiFetch, setAccessToken } from "@/lib/api";
import { toast } from "sonner";

export const AuthShell = ({ title, subtitle, children, footer }: any) => (
  <div className="min-h-screen bg-[#f6f8fb]">
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 md:px-6 h-20 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="h-8 w-8 rounded-md bg-primary text-white grid place-items-center"><Sparkles className="w-4 h-4" /></span>
          <span className="text-3xl font-black tracking-tight">Shobar Shonge</span>
        </Link>
        <div className="flex items-center gap-2">
          <Link to="/login"><Button variant="outline" className="hidden md:inline-flex">Log in</Button></Link>
          <Link to="/dashboard"><Button className="bg-primary hover:bg-primary/90">Open Dashboard</Button></Link>
        </div>
      </div>
    </header>

    <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-8 px-4 md:px-6 py-10 md:py-16">
      <div className="hidden lg:flex relative bg-[#1d2450] rounded-2xl p-12 flex-col justify-between text-white overflow-hidden">
        <div className="absolute top-20 -right-20 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-float" />
        <Link to="/" className="flex items-center gap-2 relative">
          <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="font-bold text-xl">Shobar Shonge</span>
        </Link>
        <div className="relative">
          <h2 className="text-4xl font-bold leading-tight mb-4">"Support your customers faster with one unified platform."</h2>
          <p className="text-white/80">Rashed Hossain, Founder</p>
        </div>
<<<<<<< HEAD
        <div className="text-xs text-white/60 relative">2026 Shobar Shonge - Bangladesh</div>
=======
        <div className="text-xs text-white/60 relative">© 2026 Shobar Shonge · Bangladesh</div>
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a
      </div>

      <div className="flex items-center justify-center p-6 md:p-12 bg-transparent">
        <div className="w-full max-w-md animate-fade-in-up">
          <Link to="/" className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center"><Sparkles className="w-5 h-5 text-white" /></div>
            <span className="font-bold text-lg">Shobar Shonge</span>
          </Link>
          <h1 className="text-3xl font-bold mb-2">{title}</h1>
          <p className="text-muted-foreground mb-8">{subtitle}</p>
          {children}
          {footer && <div className="mt-6 text-center text-sm text-muted-foreground">{footer}</div>}
        </div>
      </div>
    </div>
  </div>
);

export default function Login() {
  const nav = useNavigate();
<<<<<<< HEAD
  const [googleConfigured, setGoogleConfigured] = useState<boolean | null>(null);
  const [googleDevFallback, setGoogleDevFallback] = useState(false);
  const [googleMissing, setGoogleMissing] = useState<string[]>([]);

  useEffect(() => {
    const loadGoogleStatus = async () => {
      try {
        const status = await apiFetch<{ configured: boolean; missing: string[]; dev_fallback_available?: boolean }>("/api/accounts/google/status/");
        setGoogleConfigured(Boolean(status.configured));
        setGoogleDevFallback(Boolean(status.dev_fallback_available));
        setGoogleMissing(status.missing || []);
      } catch {
        setGoogleConfigured(false);
      }
    };
    loadGoogleStatus();
  }, []);

  const handleGoogleContinue = async () => {
    try {
      const payload = await apiFetch<{ auth_url: string }>("/api/accounts/google/start/");
      if (!payload?.auth_url) {
        toast.error("Google login is not configured yet.");
        return;
      }
      window.location.href = payload.auth_url;
    } catch (e: any) {
      if (googleMissing.length) {
        toast.error(`Google login not configured: ${googleMissing.join(", ")}`);
      } else {
        toast.error(e?.message || "Google login is not configured yet.");
      }
    }
  };
=======
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Log in to your Shobar Shonge dashboard"
      footer={<>Don't have an account? <Link to="/register" className="text-primary font-medium hover:underline">Sign up</Link></>}
    >
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          const form = e.currentTarget;
          const formData = new FormData(form);
          const username = String(formData.get("email") || "").trim();
          const password = String(formData.get("password") || "");

          try {
            const payload = await apiFetch<{ tokens: { access: string; refresh: string } }>("/api/accounts/login/", {
              method: "POST",
              body: JSON.stringify({ username, password }),
            });
            setAccessToken(payload.tokens.access);
            localStorage.setItem("refresh_token", payload.tokens.refresh);
            toast.success("Login successful");
            nav("/dashboard");
          } catch {
            toast.error("Login failed. Check username/password.");
          }
        }}
        className="space-y-4"
      >
        <div className="space-y-2">
          <Label>Email / Username</Label>
          <Input name="email" type="text" placeholder="owner@supportbond.ai" defaultValue="owner@supportbond.ai" required />
        </div>
        <div className="space-y-2">
          <div className="flex justify-between">
            <Label>Password</Label>
            <Link to="/forgot-password" className="text-xs text-primary hover:underline">Forgot password?</Link>
          </div>
          <Input name="password" type="password" placeholder="********" defaultValue="password123" required />
        </div>
        <Button type="submit" className="w-full gradient-primary border-0 shadow-glow h-11">Log in to Dashboard</Button>
        <Button type="button" variant="outline" className="w-full h-11" onClick={handleGoogleContinue} disabled={googleConfigured === false && !googleDevFallback}>Continue with Google</Button>
        {googleConfigured === false && (
          <p className="text-xs text-muted-foreground">
            Google login setup required: {googleMissing.length ? googleMissing.join(", ") : "missing backend OAuth config"}.
            {googleDevFallback ? " Dev fallback is enabled for local testing." : ""}
          </p>
        )}
      </form>
    </AuthShell>
  );
}
