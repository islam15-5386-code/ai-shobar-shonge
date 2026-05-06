import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthShell } from "./Login";

export default function ForgotPassword() {
  return (
    <AuthShell
      title="Forgot password?"
      subtitle="Enter your email and we'll send you a reset link."
      footer={<><Link to="/login" className="text-primary font-medium hover:underline">← Back to login</Link></>}
    >
      <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
        <div className="space-y-2"><Label>Email</Label><Input type="email" placeholder="you@business.com" required /></div>
        <Button type="submit" className="w-full gradient-primary border-0 shadow-glow h-11">Send reset link</Button>
      </form>
    </AuthShell>
  );
}
