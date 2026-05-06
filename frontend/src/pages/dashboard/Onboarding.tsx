import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ShoppingBag, GraduationCap, Stethoscope, Wrench, Upload, ArrowRight, Check } from "lucide-react";
import { Sparkles } from "lucide-react";

const categories = [
  { id: "shop", label: "Online Shop", icon: ShoppingBag },
  { id: "coaching", label: "Coaching Center", icon: GraduationCap },
  { id: "clinic", label: "Clinic", icon: Stethoscope },
  { id: "service", label: "Service Business", icon: Wrench },
];

export default function Onboarding() {
  const [step, setStep] = useState(1);
  const [category, setCategory] = useState("shop");
  const nav = useNavigate();

  return (
    <div className="min-h-screen gradient-soft py-10 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center"><Sparkles className="w-5 h-5 text-white" /></div>
          <span className="font-bold text-lg">Shobar Shonge Setup</span>
        </div>

        {/* Stepper */}
        <div className="flex items-center justify-between mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex-1 flex items-center">
              <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${step >= s ? "gradient-primary text-white shadow-glow" : "bg-muted text-muted-foreground"}`}>
                {step > s ? <Check className="w-4 h-4" /> : s}
              </div>
              {s < 3 && <div className={`flex-1 h-0.5 mx-2 ${step > s ? "bg-primary" : "bg-border"}`} />}
            </div>
          ))}
        </div>

        <Card className="p-8 shadow-elegant border-0 animate-fade-in-up">
          {step === 1 && (
            <>
              <h2 className="text-2xl font-bold mb-1">Tell us about your business</h2>
              <p className="text-muted-foreground mb-6">We'll personalize your AI based on your business type.</p>
              <div className="space-y-5">
                <div className="space-y-2"><Label>Business name</Label><Input placeholder="e.g. Trendy BD" /></div>
                <div className="space-y-2">
                  <Label>Category</Label>
                  <div className="grid grid-cols-2 gap-3">
                    {categories.map((c) => (
                      <button key={c.id} onClick={() => setCategory(c.id)} className={`p-4 rounded-xl border-2 text-left transition-all ${category === c.id ? "border-primary bg-primary/5 shadow-md" : "border-border hover:border-primary/40"}`}>
                        <c.icon className={`w-6 h-6 mb-2 ${category === c.id ? "text-primary" : "text-muted-foreground"}`} />
                        <div className="font-medium text-sm">{c.label}</div>
                      </button>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Logo</Label>
                  <div className="border-2 border-dashed rounded-xl p-8 text-center hover:border-primary transition cursor-pointer">
                    <Upload className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                    <div className="text-sm">Click to upload logo</div>
                    <div className="text-xs text-muted-foreground">PNG, JPG up to 2MB</div>
                  </div>
                </div>
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <h2 className="text-2xl font-bold mb-1">Contact & hours</h2>
              <p className="text-muted-foreground mb-6">How can customers reach you?</p>
              <div className="space-y-5">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2"><Label>Support email</Label><Input type="email" placeholder="support@business.com" /></div>
                  <div className="space-y-2"><Label>Phone</Label><Input placeholder="+8801XXXXXXXXX" /></div>
                </div>
                <div className="space-y-2"><Label>Business hours</Label><Input placeholder="9:00 AM - 9:00 PM" defaultValue="9:00 AM - 9:00 PM" /></div>
                <div className="space-y-2"><Label>Address</Label><Textarea placeholder="Shop address" rows={2} /></div>
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <h2 className="text-2xl font-bold mb-1">AI preferences</h2>
              <p className="text-muted-foreground mb-6">Pick how your AI should communicate.</p>
              <div className="space-y-5">
                <div className="space-y-2">
                  <Label>Preferred language</Label>
                  <Select defaultValue="mixed"><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
                    <SelectItem value="bangla">বাংলা (Bangla)</SelectItem>
                    <SelectItem value="english">English</SelectItem>
                    <SelectItem value="mixed">Mixed (Banglish + English)</SelectItem>
                  </SelectContent></Select>
                </div>
                <div className="space-y-2">
                  <Label>Business tone</Label>
                  <Select defaultValue="friendly"><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
                    <SelectItem value="friendly">Friendly</SelectItem>
                    <SelectItem value="professional">Professional</SelectItem>
                    <SelectItem value="short">Short & direct</SelectItem>
                    <SelectItem value="detailed">Detailed</SelectItem>
                  </SelectContent></Select>
                </div>
              </div>
            </>
          )}

          <div className="flex justify-between mt-8">
            <Button variant="ghost" onClick={() => step > 1 ? setStep(step - 1) : nav("/dashboard")}>{step > 1 ? "Back" : "Skip"}</Button>
            <Button className="gradient-primary border-0 shadow-glow" onClick={() => step < 3 ? setStep(step + 1) : nav("/dashboard")}>
              {step < 3 ? "Continue" : "Go to dashboard"} <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
