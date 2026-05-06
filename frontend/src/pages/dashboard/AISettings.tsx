import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { useEffect, useState } from "react";
import { Bot } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

type AISettingsPayload = {
  auto_reply_enabled: boolean;
  confidence_threshold: number;
  business_tone: string;
  language: string;
  rule_refund: boolean;
  rule_negative_sentiment: boolean;
  rule_below_confidence: boolean;
  rule_customer_requests_human: boolean;
  system_prompt: string;
};

const defaults: AISettingsPayload = {
  auto_reply_enabled: true,
  confidence_threshold: 0.75,
  business_tone: "professional",
  language: "mixed",
  rule_refund: true,
  rule_negative_sentiment: true,
  rule_below_confidence: true,
  rule_customer_requests_human: true,
  system_prompt: "",
};

export default function AISettings() {
  const [settings, setSettings] = useState<AISettingsPayload>(defaults);
  const [saving, setSaving] = useState(false);

  const loadSettings = async () => {
    try {
      const data = await apiFetch<AISettingsPayload>("/api/ai-gateway/settings/");
      setSettings({ ...defaults, ...data });
    } catch {
      toast.error("Failed to load AI settings");
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const saveSettings = async () => {
    try {
      setSaving(true);
      await apiFetch("/api/ai-gateway/settings/", {
        method: "PUT",
        body: JSON.stringify(settings),
      });
      toast.success("AI settings saved");
    } catch {
      toast.error("Failed to save AI settings");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-4 md:p-8 max-w-4xl">
      <PageHeader
        title="AI Settings"
        subtitle="Customize how your AI assistant behaves"
        actions={<Button className="gradient-primary border-0" onClick={saveSettings} disabled={saving}>{saving ? "Saving..." : "Save Changes"}</Button>}
      />

      <div className="space-y-6">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center"><Bot className="w-5 h-5 text-white" /></div>
              <div>
                <h3 className="font-semibold">Auto-reply</h3>
                <p className="text-xs text-muted-foreground">Let AI respond to incoming messages automatically</p>
              </div>
            </div>
            <Switch checked={settings.auto_reply_enabled} onCheckedChange={(v) => setSettings((s) => ({ ...s, auto_reply_enabled: v }))} />
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="font-semibold mb-1">Confidence threshold</h3>
          <p className="text-xs text-muted-foreground mb-5">AI escalates to human when confidence falls below this level.</p>
          <Slider
            value={[Math.round(settings.confidence_threshold * 100)]}
            onValueChange={(v) => setSettings((s) => ({ ...s, confidence_threshold: (v[0] || 0) / 100 }))}
            max={100}
            step={5}
          />
          <div className="flex justify-between mt-2 text-xs text-muted-foreground"><span>0%</span><span className="text-primary font-semibold">{Math.round(settings.confidence_threshold * 100)}%</span><span>100%</span></div>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6 space-y-2">
            <Label>Business tone</Label>
            <Select value={settings.business_tone} onValueChange={(v) => setSettings((s) => ({ ...s, business_tone: v }))}>
              <SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
                <SelectItem value="friendly">Friendly</SelectItem>
                <SelectItem value="professional">Professional</SelectItem>
                <SelectItem value="short">Short & direct</SelectItem>
                <SelectItem value="detailed">Detailed</SelectItem>
              </SelectContent></Select>
            <p className="text-xs text-muted-foreground">How AI should sound to customers</p>
          </Card>
          <Card className="p-6 space-y-2">
            <Label>Language</Label>
            <Select value={settings.language} onValueChange={(v) => setSettings((s) => ({ ...s, language: v }))}>
              <SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
                <SelectItem value="bangla">Bangla</SelectItem>
                <SelectItem value="english">English</SelectItem>
                <SelectItem value="mixed">Mixed (Banglish + English)</SelectItem>
              </SelectContent></Select>
            <p className="text-xs text-muted-foreground">Reply language preference</p>
          </Card>
        </div>

        <Card className="p-6">
          <h3 className="font-semibold mb-1">Escalation rules</h3>
          <p className="text-xs text-muted-foreground mb-4">When should the AI hand over to a human?</p>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b"><span className="text-sm">Customer asks for refund</span><Switch checked={settings.rule_refund} onCheckedChange={(v) => setSettings((s) => ({ ...s, rule_refund: v }))} /></div>
            <div className="flex items-center justify-between py-2 border-b"><span className="text-sm">Negative sentiment detected</span><Switch checked={settings.rule_negative_sentiment} onCheckedChange={(v) => setSettings((s) => ({ ...s, rule_negative_sentiment: v }))} /></div>
            <div className="flex items-center justify-between py-2 border-b"><span className="text-sm">Confidence below threshold</span><Switch checked={settings.rule_below_confidence} onCheckedChange={(v) => setSettings((s) => ({ ...s, rule_below_confidence: v }))} /></div>
            <div className="flex items-center justify-between py-2"><span className="text-sm">Customer requests human</span><Switch checked={settings.rule_customer_requests_human} onCheckedChange={(v) => setSettings((s) => ({ ...s, rule_customer_requests_human: v }))} /></div>
          </div>
        </Card>

        <Card className="p-6">
          <Label>Custom system prompt</Label>
          <Textarea rows={5} className="mt-2" value={settings.system_prompt} onChange={(e) => setSettings((s) => ({ ...s, system_prompt: e.target.value }))} />
        </Card>
      </div>
    </div>
  );
}
