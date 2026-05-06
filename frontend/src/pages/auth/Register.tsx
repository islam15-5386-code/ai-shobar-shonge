import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthShell } from "./Login";

export default function Register() {
  const nav = useNavigate();
  return (
    <AuthShell
      title="Create your account"
      subtitle="Start your 14-day free trial. No card needed."
      footer={<>Already have an account? <Link to="/login" className="text-primary font-medium hover:underline">Log in</Link></>}
    >
      <form onSubmit={(e) => { e.preventDefault(); nav("/dashboard/onboarding"); }} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2"><Label>First name</Label><Input placeholder="Rashed" required /></div>
          <div className="space-y-2"><Label>Last name</Label><Input placeholder="Hossain" required /></div>
        </div>
        <div className="space-y-2"><Label>Work email</Label><Input type="email" placeholder="you@business.com" required /></div>
        <div className="space-y-2"><Label>Phone</Label><Input placeholder="+8801XXXXXXXXX" /></div>
        <div className="space-y-2"><Label>Password</Label><Input type="password" placeholder="At least 8 characters" required /></div>
        <Button type="submit" className="w-full gradient-primary border-0 shadow-glow h-11">Create account</Button>
      </form>
    </AuthShell>
  );
}
