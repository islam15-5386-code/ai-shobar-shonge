import { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";
import { Plus, Search, Upload, RefreshCw, Edit2, Trash2, Sparkles } from "lucide-react";
import { toast } from "sonner";

type FAQItem = {
  id: number;
  question: string;
  answer: string;
  category?: string;
  language?: string;
  embedding_status?: string;
};

const emptyForm = { question: "", answer: "", category: "", language: "bn" };

export default function FAQs() {
  const [items, setItems] = useState<FAQItem[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [openAdd, setOpenAdd] = useState(false);
  const [form, setForm] = useState(emptyForm);

  const loadFaqs = async () => {
    try {
      setLoading(true);
      const data = await apiFetch<FAQItem[]>("/api/faqs/");
      setItems(data || []);
    } catch (e: any) {
      toast.error("FAQ load failed. Please login first.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFaqs();
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((f) => f.question.toLowerCase().includes(q) || f.answer.toLowerCase().includes(q));
  }, [items, query]);

  const handleCreate = async () => {
    if (!form.question.trim() || !form.answer.trim()) {
      toast.error("Question and answer are required");
      return;
    }
    try {
      setSaving(true);
      await apiFetch("/api/faqs/", {
        method: "POST",
        body: JSON.stringify({
          question: form.question.trim(),
          answer: form.answer.trim(),
          category: form.category.trim(),
          language: (form.language || "bn").toLowerCase().startsWith("en") ? "en" : "bn",
        }),
      });
      toast.success("FAQ added");
      setOpenAdd(false);
      setForm(emptyForm);
      await loadFaqs();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Add FAQ failed";
      toast.error(message);
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = async (f: FAQItem) => {
    const question = window.prompt("Edit question", f.question);
    if (!question) return;
    const answer = window.prompt("Edit answer", f.answer);
    if (!answer) return;
    try {
      await apiFetch(`/api/faqs/${f.id}/`, {
        method: "PATCH",
        body: JSON.stringify({ question, answer }),
      });
      toast.success("FAQ updated");
      await loadFaqs();
    } catch {
      toast.error("Update failed");
    }
  };

  const handleDelete = async (f: FAQItem) => {
    if (!window.confirm(`Delete FAQ: ${f.question}?`)) return;
    try {
      await apiFetch(`/api/faqs/${f.id}/`, { method: "DELETE" });
      toast.success("FAQ deleted");
      await loadFaqs();
    } catch {
      toast.error("Delete failed");
    }
  };

  const handleReindex = async () => {
    try {
      await apiFetch("/api/faqs/reindex/", { method: "POST", body: JSON.stringify({}) });
      toast.success("Re-index started");
      await loadFaqs();
    } catch {
      toast.error("Re-index failed");
    }
  };

  return (
    <div className="p-4 md:p-8">
      <PageHeader
        title="FAQ Knowledge Base"
        subtitle="Train your AI with common questions and answers"
        actions={
          <>
            <Button variant="outline" size="sm" onClick={() => toast.message("Bulk import এখন backend format অনুযায়ী JSON file integration লাগবে") }>
              <Upload className="w-4 h-4 mr-1" /> Bulk Import
            </Button>
            <Button variant="outline" size="sm" onClick={handleReindex}>
              <RefreshCw className="w-4 h-4 mr-1" /> Re-index AI
            </Button>
            <Dialog open={openAdd} onOpenChange={setOpenAdd}>
              <DialogTrigger asChild>
                <Button size="sm" className="gradient-primary border-0">
                  <Plus className="w-4 h-4 mr-1" /> Add FAQ
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>Add new FAQ</DialogTitle></DialogHeader>
                <div className="space-y-4">
                  <div className="space-y-2"><Label>Question</Label><Input value={form.question} onChange={(e) => setForm((p) => ({ ...p, question: e.target.value }))} /></div>
                  <div className="space-y-2"><Label>Answer</Label><Textarea rows={4} value={form.answer} onChange={(e) => setForm((p) => ({ ...p, answer: e.target.value }))} /></div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-2"><Label>Category</Label><Input value={form.category} onChange={(e) => setForm((p) => ({ ...p, category: e.target.value }))} /></div>
                    <div className="space-y-2"><Label>Language</Label><Input value={form.language} onChange={(e) => setForm((p) => ({ ...p, language: e.target.value }))} /></div>
                  </div>
                  <Button className="w-full gradient-primary border-0" onClick={handleCreate} disabled={saving}>{saving ? "Saving..." : "Save FAQ"}</Button>
                </div>
              </DialogContent>
            </Dialog>
          </>
        }
      />

      <Card className="p-5 mb-4 bg-primary/5 border-primary/20 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center"><Sparkles className="w-5 h-5 text-white" /></div>
        <div className="flex-1">
          <div className="font-semibold text-sm">AI knowledge is up to date</div>
          <div className="text-xs text-muted-foreground">{loading ? "Loading..." : `${items.length} entries`}</div>
        </div>
        <Badge variant="outline" className="bg-success/10 text-success border-success/20">Active</Badge>
      </Card>

      <Card>
        <div className="p-4 border-b flex items-center gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input placeholder="Search FAQs..." className="pl-9 bg-muted/50 border-0" value={query} onChange={(e) => setQuery(e.target.value)} />
          </div>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Question</TableHead>
              <TableHead className="hidden md:table-cell">Category</TableHead>
              <TableHead className="hidden md:table-cell">Language</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((f) => (
              <TableRow key={f.id} className="hover:bg-muted/30">
                <TableCell>
                  <div className="font-medium font-bangla">{f.question}</div>
                  <div className="text-xs text-muted-foreground truncate max-w-md font-bangla mt-0.5">{f.answer}</div>
                </TableCell>
                <TableCell className="hidden md:table-cell"><Badge variant="outline">{f.category || "General"}</Badge></TableCell>
                <TableCell className="hidden md:table-cell"><Badge variant="secondary">{f.language || "Bangla"}</Badge></TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="icon" className="w-8 h-8" onClick={() => handleEdit(f)}><Edit2 className="w-3.5 h-3.5" /></Button>
                  <Button variant="ghost" size="icon" className="w-8 h-8 text-destructive" onClick={() => handleDelete(f)}><Trash2 className="w-3.5 h-3.5" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
