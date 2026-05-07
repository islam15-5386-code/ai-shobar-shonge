import { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { API_BASE_URL, apiFetch } from "@/lib/api";
import { Globe, MessageCircle, Phone, Copy, Check } from "lucide-react";
import { toast } from "sonner";

export default function Integrations() {
  const [activeTab, setActiveTab] = useState("web");
  const [messengerConnected, setMessengerConnected] = useState(false);
  const [whatsAppConnected, setWhatsAppConnected] = useState(false);

  const [messengerForm, setMessengerForm] = useState({
    page_id: "",
    page_access_token: "",
    verify_token: "",
    app_id: "",
    app_secret: "",
  });

  const [waForm, setWaForm] = useState({
    phone_number_id: "",
    access_token: "",
    verify_token: "",
    waba_id: "",
  });
<<<<<<< HEAD
  const [waSend, setWaSend] = useState({
    to_number: "",
    text: "",
    recipients_csv: "",
  });
=======
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a

  const webhookBase = useMemo(() => API_BASE_URL, []);

  const loadSetup = async () => {
    try {
      const m = await apiFetch<any>("/api/integrations/messenger/setup/");
      setMessengerConnected(Boolean(m?.is_active));
      setMessengerForm((s) => ({
        ...s,
        page_id: m?.page_id || "",
        app_id: m?.app_id || "",
        verify_token: m?.verify_token || "",
      }));
    } catch {
      setMessengerConnected(false);
    }

    try {
      const w = await apiFetch<any>("/api/integrations/whatsapp/setup/");
      setWhatsAppConnected(Boolean(w?.is_active));
      setWaForm((s) => ({
        ...s,
        phone_number_id: w?.phone_number_id || "",
        verify_token: w?.verify_token || "",
        waba_id: w?.waba_id || "",
      }));
    } catch {
      setWhatsAppConnected(false);
    }
  };

  useEffect(() => {
    loadSetup();
  }, []);

  const copyText = async (text: string) => {
    await navigator.clipboard.writeText(text);
    toast.success("Copied");
  };

  const saveMessenger = async () => {
    if (!messengerForm.page_id || !messengerForm.page_access_token || !messengerForm.verify_token) {
      toast.error("page_id, page_access_token, verify_token required");
      return;
    }
    try {
      await apiFetch("/api/integrations/messenger/setup/", {
        method: "POST",
        body: JSON.stringify(messengerForm),
      });
      toast.success("Messenger integration saved");
      setMessengerConnected(true);
      await loadSetup();
    } catch {
      toast.error("Messenger save failed");
    }
  };

  const saveWhatsApp = async () => {
    if (!waForm.phone_number_id || !waForm.access_token || !waForm.verify_token) {
      toast.error("phone_number_id, access_token, verify_token required");
      return;
    }
    try {
      await apiFetch("/api/integrations/whatsapp/setup/", {
        method: "POST",
        body: JSON.stringify(waForm),
      });
      toast.success("WhatsApp integration saved");
      setWhatsAppConnected(true);
      await loadSetup();
    } catch {
      toast.error("WhatsApp save failed");
    }
  };

<<<<<<< HEAD
  const checkWhatsAppConnection = async () => {
    try {
      const payload = await apiFetch<any>("/api/integrations/whatsapp/status/");
      const label = payload?.display_phone_number || payload?.phone_number_id || "WhatsApp";
      toast.success(`Connected: ${label}`);
    } catch (e: any) {
      toast.error(e?.message || "WhatsApp check failed");
    }
  };

  const sendWhatsAppMessage = async () => {
    if (!waSend.to_number.trim() || !waSend.text.trim()) {
      toast.error("to number and message required");
      return;
    }
    try {
      await apiFetch("/api/integrations/whatsapp/send/", {
        method: "POST",
        body: JSON.stringify({ to_number: waSend.to_number.trim(), text: waSend.text.trim() }),
      });
      toast.success("WhatsApp message sent");
    } catch (e: any) {
      toast.error(e?.message || "Send failed");
    }
  };

  const sendWhatsAppBulk = async () => {
    const recipients = waSend.recipients_csv
      .split(/[,\n]/)
      .map((x) => x.trim())
      .filter(Boolean);
    if (!recipients.length || !waSend.text.trim()) {
      toast.error("recipients and message required");
      return;
    }
    try {
      const res = await apiFetch<any>("/api/integrations/whatsapp/bulk-send/", {
        method: "POST",
        body: JSON.stringify({ recipients, text: waSend.text.trim() }),
      });
      toast.success(`Bulk done: ${res?.sent || 0} sent, ${res?.failed || 0} failed`);
    } catch (e: any) {
      toast.error(e?.message || "Bulk send failed");
    }
  };

=======
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a
  return (
    <div className="p-4 md:p-8">
      <PageHeader title="Integrations" subtitle="Connect channels where your customers reach out" />

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <Card className="p-5 hover:shadow-elegant transition-all">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-md">
              <MessageCircle className="w-6 h-6 text-white" />
            </div>
            {messengerConnected ? (
              <Badge variant="outline" className="bg-success/10 text-success border-success/20"><Check className="w-3 h-3 mr-1" /> Connected</Badge>
            ) : (
              <Badge variant="outline">Not connected</Badge>
            )}
          </div>
          <h3 className="font-semibold mb-1">Facebook Messenger</h3>
          <p className="text-xs text-muted-foreground mb-4">Reply to FB page messages automatically</p>
          <Button className="w-full" variant={messengerConnected ? "outline" : "default"} onClick={() => setActiveTab("messenger")}>
            {messengerConnected ? "Manage" : "Connect"}
          </Button>
        </Card>

        <Card className="p-5 hover:shadow-elegant transition-all">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-md">
              <Phone className="w-6 h-6 text-white" />
            </div>
            {whatsAppConnected ? (
              <Badge variant="outline" className="bg-success/10 text-success border-success/20"><Check className="w-3 h-3 mr-1" /> Connected</Badge>
            ) : (
              <Badge variant="outline">Not connected</Badge>
            )}
          </div>
          <h3 className="font-semibold mb-1">WhatsApp Cloud API</h3>
          <p className="text-xs text-muted-foreground mb-4">WhatsApp Business messaging</p>
          <Button className="w-full" variant={whatsAppConnected ? "outline" : "default"} onClick={() => setActiveTab("whatsapp")}>
            {whatsAppConnected ? "Manage" : "Connect"}
          </Button>
        </Card>

        <Card className="p-5 hover:shadow-elegant transition-all">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center shadow-md">
              <Globe className="w-6 h-6 text-white" />
            </div>
            <Badge variant="outline">Not connected</Badge>
          </div>
          <h3 className="font-semibold mb-1">Website Chat Widget</h3>
          <p className="text-xs text-muted-foreground mb-4">Embeddable chatbot for your website</p>
          <Button className="w-full" onClick={() => setActiveTab("web")}>Connect</Button>
        </Card>
      </div>

      <Card className="p-6">
        <h3 className="font-semibold mb-1">Setup details</h3>
        <p className="text-sm text-muted-foreground mb-5">Use the credentials below to configure your integrations.</p>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="web">Website Widget</TabsTrigger>
            <TabsTrigger value="messenger">Messenger</TabsTrigger>
            <TabsTrigger value="whatsapp">WhatsApp</TabsTrigger>
          </TabsList>

          <TabsContent value="web" className="space-y-4 pt-5">
            <div className="space-y-2">
              <Label>Embed snippet</Label>
              <div className="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-xs overflow-x-auto">
                {`<script src=\"https://cdn.supportbond.ai/widget.js\" data-key=\"sk_live_demo\"></script>`}
              </div>
            </div>
            <div className="space-y-2">
              <Label>Webhook URL</Label>
              <div className="flex gap-2">
                <Input readOnly value={`${webhookBase}/api/ai-gateway/website-chat/`} className="font-mono text-xs" />
                <Button variant="outline" size="icon" onClick={() => copyText(`${webhookBase}/api/ai-gateway/website-chat/`)}><Copy className="w-4 h-4" /></Button>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="messenger" className="space-y-4 pt-5">
            <div className="space-y-2"><Label>Page ID</Label><Input value={messengerForm.page_id} onChange={(e) => setMessengerForm((s) => ({ ...s, page_id: e.target.value }))} placeholder="123456789" /></div>
            <div className="space-y-2"><Label>Page Access Token</Label><Input type="password" value={messengerForm.page_access_token} onChange={(e) => setMessengerForm((s) => ({ ...s, page_access_token: e.target.value }))} placeholder="EAA..." /></div>
            <div className="space-y-2"><Label>Verify Token</Label><Input value={messengerForm.verify_token} onChange={(e) => setMessengerForm((s) => ({ ...s, verify_token: e.target.value }))} placeholder="verify_token" /></div>
            <div className="space-y-2"><Label>Webhook URL</Label><div className="flex gap-2"><Input readOnly value={`${webhookBase}/api/integrations/messenger/webhook/`} className="font-mono text-xs" /><Button variant="outline" size="icon" onClick={() => copyText(`${webhookBase}/api/integrations/messenger/webhook/`)}><Copy className="w-4 h-4" /></Button></div></div>
            <Button className="gradient-primary border-0" onClick={saveMessenger}>Save Connection</Button>
          </TabsContent>

          <TabsContent value="whatsapp" className="space-y-4 pt-5">
            <div className="space-y-2"><Label>Phone Number ID</Label><Input value={waForm.phone_number_id} onChange={(e) => setWaForm((s) => ({ ...s, phone_number_id: e.target.value }))} placeholder="106540..." /></div>
            <div className="space-y-2"><Label>Permanent Access Token</Label><Input type="password" value={waForm.access_token} onChange={(e) => setWaForm((s) => ({ ...s, access_token: e.target.value }))} placeholder="EAA..." /></div>
            <div className="space-y-2"><Label>Verify Token</Label><Input value={waForm.verify_token} onChange={(e) => setWaForm((s) => ({ ...s, verify_token: e.target.value }))} placeholder="verify_token" /></div>
            <div className="space-y-2"><Label>Webhook URL</Label><div className="flex gap-2"><Input readOnly value={`${webhookBase}/api/integrations/whatsapp/webhook/`} className="font-mono text-xs" /><Button variant="outline" size="icon" onClick={() => copyText(`${webhookBase}/api/integrations/whatsapp/webhook/`)}><Copy className="w-4 h-4" /></Button></div></div>
<<<<<<< HEAD
            <div className="flex gap-2">
              <Button className="gradient-primary border-0" onClick={saveWhatsApp}>Save Connection</Button>
              <Button variant="outline" onClick={checkWhatsAppConnection}>Check Connection</Button>
            </div>

            <Card className="p-4 space-y-3">
              <h4 className="font-semibold">Send WhatsApp Message</h4>
              <div className="space-y-2"><Label>To Number (with country code)</Label><Input value={waSend.to_number} onChange={(e) => setWaSend((s) => ({ ...s, to_number: e.target.value }))} placeholder="8801XXXXXXXXX" /></div>
              <div className="space-y-2"><Label>Message</Label><Input value={waSend.text} onChange={(e) => setWaSend((s) => ({ ...s, text: e.target.value }))} placeholder="Hello from Shobar Shonge" /></div>
              <Button onClick={sendWhatsAppMessage}>Send Single</Button>
            </Card>

            <Card className="p-4 space-y-3">
              <h4 className="font-semibold">Bulk Send</h4>
              <div className="space-y-2"><Label>Recipients (comma or new line)</Label><Input value={waSend.recipients_csv} onChange={(e) => setWaSend((s) => ({ ...s, recipients_csv: e.target.value }))} placeholder="8801XXXXXXXXX,8801YYYYYYYYY" /></div>
              <div className="space-y-2"><Label>Message</Label><Input value={waSend.text} onChange={(e) => setWaSend((s) => ({ ...s, text: e.target.value }))} placeholder="Promo or update message" /></div>
              <Button variant="outline" onClick={sendWhatsAppBulk}>Send Bulk</Button>
            </Card>
=======
            <Button className="gradient-primary border-0" onClick={saveWhatsApp}>Save Connection</Button>
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
}
