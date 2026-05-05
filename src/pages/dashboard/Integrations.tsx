import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { Globe, MessageCircle, Phone, Copy, Check } from "lucide-react";

const integrations = [
  { id: "messenger", name: "Facebook Messenger", desc: "Reply to FB page messages automatically", icon: MessageCircle, color: "from-blue-500 to-blue-600", connected: true },
  { id: "whatsapp", name: "WhatsApp Cloud API", desc: "WhatsApp Business messaging", icon: Phone, color: "from-green-500 to-emerald-600", connected: true },
  { id: "web", name: "Website Chat Widget", desc: "Embeddable chatbot for your website", icon: Globe, color: "from-violet-500 to-fuchsia-600", connected: false },
];

export default function Integrations() {
  return (
    <div className="p-4 md:p-8">
      <PageHeader title="Integrations" subtitle="Connect channels where your customers reach out" />

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        {integrations.map((i) => (
          <Card key={i.id} className="p-5 hover:shadow-elegant transition-all">
            <div className="flex items-start justify-between mb-4">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${i.color} flex items-center justify-center shadow-md`}>
                <i.icon className="w-6 h-6 text-white" />
              </div>
              {i.connected ? <Badge variant="outline" className="bg-success/10 text-success border-success/20"><Check className="w-3 h-3 mr-1" /> Connected</Badge> : <Badge variant="outline">Not connected</Badge>}
            </div>
            <h3 className="font-semibold mb-1">{i.name}</h3>
            <p className="text-xs text-muted-foreground mb-4">{i.desc}</p>
            <Button className="w-full" variant={i.connected ? "outline" : "default"}>{i.connected ? "Manage" : "Connect"}</Button>
          </Card>
        ))}
      </div>

      <Card className="p-6">
        <h3 className="font-semibold mb-1">Setup details</h3>
        <p className="text-sm text-muted-foreground mb-5">Use the credentials below to configure your integrations.</p>

        <Tabs defaultValue="web">
          <TabsList>
            <TabsTrigger value="web">Website Widget</TabsTrigger>
            <TabsTrigger value="messenger">Messenger</TabsTrigger>
            <TabsTrigger value="whatsapp">WhatsApp</TabsTrigger>
          </TabsList>
          <TabsContent value="web" className="space-y-4 pt-5">
            <div className="space-y-2">
              <Label>Embed snippet</Label>
              <div className="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-xs overflow-x-auto">
                {`<script src="https://cdn.sahaj.ai/widget.js" data-key="sk_live_a8b2c4d6..."></script>`}
              </div>
            </div>
            <div className="space-y-2"><Label>API Key</Label><div className="flex gap-2"><Input readOnly value="sk_live_a8b2c4d6e8f0g2h4i6j8k0l2m4n6o8p0" className="font-mono text-xs" /><Button variant="outline" size="icon"><Copy className="w-4 h-4" /></Button></div></div>
            <div className="space-y-2"><Label>Webhook URL</Label><div className="flex gap-2"><Input readOnly value="https://api.sahaj.ai/webhooks/web/u_4521" className="font-mono text-xs" /><Button variant="outline" size="icon"><Copy className="w-4 h-4" /></Button></div></div>
          </TabsContent>
          <TabsContent value="messenger" className="space-y-4 pt-5">
            <div className="space-y-2"><Label>Page Access Token</Label><Input placeholder="EAA..." /></div>
            <div className="space-y-2"><Label>Verify Token</Label><Input readOnly value="sahaj_verify_x9k2m4" className="font-mono text-xs" /></div>
            <div className="space-y-2"><Label>Webhook URL</Label><Input readOnly value="https://api.sahaj.ai/webhooks/messenger/u_4521" className="font-mono text-xs" /></div>
            <Button className="gradient-primary border-0">Save & Test Connection</Button>
          </TabsContent>
          <TabsContent value="whatsapp" className="space-y-4 pt-5">
            <div className="space-y-2"><Label>Phone Number ID</Label><Input placeholder="106540..." /></div>
            <div className="space-y-2"><Label>Permanent Access Token</Label><Input placeholder="EAA..." type="password" /></div>
            <div className="space-y-2"><Label>Webhook URL</Label><Input readOnly value="https://api.sahaj.ai/webhooks/whatsapp/u_4521" className="font-mono text-xs" /></div>
            <Button className="gradient-primary border-0">Save & Test Connection</Button>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
}
