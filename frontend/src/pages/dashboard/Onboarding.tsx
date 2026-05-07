import { useNavigate } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ShoppingBag, GraduationCap, Stethoscope, Wrench, Upload, ArrowRight, Check } from "lucide-react";
import { Sparkles } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

const categories = [
  { id: "shop", label: "Online Shop", icon: ShoppingBag },
  { id: "coaching", label: "Coaching Center", icon: GraduationCap },
  { id: "clinic", label: "Clinic", icon: Stethoscope },
  { id: "service", label: "Service Business", icon: Wrench },
];

type BusinessSetupPayload = {
  name: string;
  slug: string;
  website: string;
  welcome_message: string;
  handover_enabled: boolean;
  category: string;
  support_email: string;
  support_phone: string;
  business_hours: string;
  address: string;
  logo_url?: string;
};

type AISettingsPayload = {
  business_tone: string;
  language: string;
};

const defaultData: BusinessSetupPayload = {
  name: "",
  slug: "",
  website: "",
  welcome_message: "Hello! How can I help you today?",
  handover_enabled: true,
  category: "shop",
  support_email: "",
  support_phone: "",
  business_hours: "9:00 AM - 9:00 PM",
  address: "",
  logo_url: "",
};

function toSlug(name: string) {
  return name.toLowerCase().trim().replace(/[^a-z0-9\s-]/g, "").replace(/\s+/g, "-").replace(/-+/g, "-");
}

export default function Onboarding() {
  const [step, setStep] = useState(1);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [business, setBusiness] = useState<BusinessSetupPayload>(defaultData);
  const [aiPrefs, setAiPrefs] = useState<AISettingsPayload>({ business_tone: "friendly", language: "mixed" });
  const fileRef = useRef<HTMLInputElement | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      try {
        const b = await apiFetch<BusinessSetupPayload>("/api/businesses/setup/");
        setBusiness((prev) => ({ ...prev, ...b }));
      } catch {
        // ignore if business not created yet
      }
      try {
        const ai = await apiFetch<any>("/api/ai-gateway/settings/");
        setAiPrefs({
          business_tone: ai.business_tone || "friendly",
          language: ai.language || "mixed",
        });
      } catch {
        // ignore optional
      }
    };
    loadData();
  }, []);

  const saveBusiness = async () => {
    const payload = {
      ...business,
      slug: business.slug || toSlug(business.name),
    };
    const method = payload.name && payload.slug ? "POST" : "PATCH";
    return apiFetch<BusinessSetupPayload>("/api/businesses/setup/", {
      method,
      body: JSON.stringify(payload),
    });
  };

  const handleUpload = async (file?: File) => {
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      toast.error("Logo must be 2MB or smaller");
      return;
    }
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("logo", file);
      const res = await apiFetch<{ logo_url: string; extracted_data: any }>("/api/businesses/upload-logo/", {
        method: "POST",
        body: fd,
      });

      setBusiness((prev) => {
        const next = { ...prev, logo_url: res.logo_url };
        const suggestedName = res.extracted_data?.suggested_business_name || "";
        const suggestedCategory = res.extracted_data?.suggested_category || "";
        if (!prev.name && suggestedName) next.name = suggestedName;
        if (suggestedCategory) next.category = suggestedCategory;
        if (!prev.slug && next.name) next.slug = toSlug(next.name);
        return next;
      });

      if (res.extracted_data?.detected_text) {
        toast.success("Logo uploaded. Text detected from image.");
      } else {
        toast.success("Logo uploaded successfully.");
      }
    } catch {
      toast.error("Logo upload failed");
    } finally {
      setUploading(false);
    }
  };

  const onContinue = async () => {
    try {
      setSaving(true);
      if (step === 1 || step === 2) {
        const saved = await saveBusiness();
        setBusiness((prev) => ({ ...prev, ...saved }));
      }
      if (step === 3) {
        await apiFetch("/api/ai-gateway/settings/", {
          method: "PUT",
          body: JSON.stringify(aiPrefs),
        });
        toast.success("Setup completed");
        nav("/dashboard");
        return;
      }
      setStep((s) => s + 1);
    } catch (e: any) {
      toast.error("Could not save setup data");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen gradient-soft py-10 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center"><Sparkles className="w-5 h-5 text-white" /></div>
          <span className="font-bold text-lg">Shobar Shonge Setup</span>
        </div>

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
                <div className="space-y-2">
                  <Label>Business name</Label>
                  <Input placeholder="e.g. Trendy BD" value={business.name} onChange={(e) => setBusiness((p) => ({ ...p, name: e.target.value, slug: toSlug(e.target.value) }))} />
                </div>
                <div className="space-y-2">
                  <Label>Category</Label>
                  <div className="grid grid-cols-2 gap-3">
                    {categories.map((c) => (
                      <button key={c.id} onClick={() => setBusiness((p) => ({ ...p, category: c.id }))} className={`p-4 rounded-xl border-2 text-left transition-all ${business.category === c.id ? "border-primary bg-primary/5 shadow-md" : "border-border hover:border-primary/40"}`}>
                        <c.icon className={`w-6 h-6 mb-2 ${business.category === c.id ? "text-primary" : "text-muted-foreground"}`} />
                        <div className="font-medium text-sm">{c.label}</div>
                      </button>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Logo</Label>
                  <input ref={fileRef} type="file" accept="image/png,image/jpeg,image/jpg" className="hidden" onChange={(e) => handleUpload(e.target.files?.[0])} />
                  <div className="border-2 border-dashed rounded-xl p-8 text-center hover:border-primary transition cursor-pointer" onClick={() => fileRef.current?.click()}>
                    {business.logo_url ? (
                      <img src={business.logo_url} alt="Logo" className="max-h-24 mx-auto mb-2 rounded" />
                    ) : (
                      <Upload className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                    )}
                    <div className="text-sm">{uploading ? "Uploading..." : "Click to upload logo"}</div>
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
                  <div className="space-y-2"><Label>Support email</Label><Input type="email" placeholder="support@business.com" value={business.support_email} onChange={(e) => setBusiness((p) => ({ ...p, support_email: e.target.value }))} /></div>
                  <div className="space-y-2"><Label>Phone</Label><Input placeholder="+8801XXXXXXXXX" value={business.support_phone} onChange={(e) => setBusiness((p) => ({ ...p, support_phone: e.target.value }))} /></div>
                </div>
                <div className="space-y-2"><Label>Business hours</Label><Input placeholder="9:00 AM - 9:00 PM" value={business.business_hours} onChange={(e) => setBusiness((p) => ({ ...p, business_hours: e.target.value }))} /></div>
                <div className="space-y-2"><Label>Address</Label><Textarea placeholder="Shop address" rows={2} value={business.address} onChange={(e) => setBusiness((p) => ({ ...p, address: e.target.value }))} /></div>
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
                  <Select value={aiPrefs.language} onValueChange={(v) => setAiPrefs((p) => ({ ...p, language: v }))}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
                    <SelectItem value="bangla">বাংলা (Bangla)</SelectItem>
                    <SelectItem value="english">English</SelectItem>
                    <SelectItem value="mixed">Mixed (Banglish + English)</SelectItem>
                  </SelectContent></Select>
                </div>
                <div className="space-y-2">
                  <Label>Business tone</Label>
                  <Select value={aiPrefs.business_tone} onValueChange={(v) => setAiPrefs((p) => ({ ...p, business_tone: v }))}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
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
            <Button className="gradient-primary border-0 shadow-glow" onClick={onContinue} disabled={saving || uploading}>
              {step < 3 ? "Continue" : "Go to dashboard"} <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
