import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { useState } from "react";
import { Bot } from "lucide-react";

export default function AISettings() {
  const [conf, setConf] = useState([75]);
  return (
    <div className="p-4 md:p-8 max-w-4xl">
      <PageHeader title="AI Settings" subtitle="Customize how your AI assistant behaves" actions={<Button className="gradient-primary border-0">Save Changes</Button>} />

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
            <Switch defaultChecked />
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="font-semibold mb-1">Confidence threshold</h3>
          <p className="text-xs text-muted-foreground mb-5">AI escalates to human when confidence falls below this level.</p>
          <Slider value={conf} onValueChange={setConf} max={100} step={5} />
          <div className="flex justify-between mt-2 text-xs text-muted-foreground"><span>0%</span><span className="text-primary font-semibold">{conf[0]}%</span><span>100%</span></div>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6 space-y-2">
            <Label>Business tone</Label>
            <Select defaultValue="friendly"><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
              <SelectItem value="friendly">😊 Friendly</SelectItem>
              <SelectItem value="professional">👔 Professional</SelectItem>
              <SelectItem value="short">⚡ Short & direct</SelectItem>
              <SelectItem value="detailed">📝 Detailed</SelectItem>
            </SelectContent></Select>
            <p className="text-xs text-muted-foreground">How AI should sound to customers</p>
          </Card>
          <Card className="p-6 space-y-2">
            <Label>Language</Label>
            <Select defaultValue="mixed"><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
              <SelectItem value="bangla">বাংলা</SelectItem>
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
            {["Customer asks for refund", "Negative sentiment detected", "Confidence below threshold", "Customer requests human"].map((r) => (
              <div key={r} className="flex items-center justify-between py-2 border-b last:border-0">
                <span className="text-sm">{r}</span>
                <Switch defaultChecked />
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <Label>Custom system prompt</Label>
          <Textarea rows={5} className="mt-2" defaultValue="You are a helpful customer support assistant for Trendy BD, a fashion store in Dhaka. Always be polite, suggest products, and offer free home delivery on orders above ৳1,500." />
        </Card>
      </div>
    </div>
  );
}
