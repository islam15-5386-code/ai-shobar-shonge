import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { faqs } from "@/lib/mockData";
import { Plus, Search, Upload, RefreshCw, Edit2, Trash2, Sparkles } from "lucide-react";

export default function FAQs() {
  return (
    <div className="p-4 md:p-8">
      <PageHeader
        title="FAQ Knowledge Base"
        subtitle="Train your AI with common questions and answers"
        actions={<>
          <Button variant="outline" size="sm"><Upload className="w-4 h-4 mr-1" /> Bulk Import</Button>
          <Button variant="outline" size="sm"><RefreshCw className="w-4 h-4 mr-1" /> Re-index AI</Button>
          <Dialog>
            <DialogTrigger asChild><Button size="sm" className="gradient-primary border-0"><Plus className="w-4 h-4 mr-1" /> Add FAQ</Button></DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Add new FAQ</DialogTitle></DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2"><Label>Question</Label><Input placeholder="e.g. What is the delivery time?" /></div>
                <div className="space-y-2"><Label>Answer</Label><Textarea rows={4} placeholder="Detailed answer..." /></div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2"><Label>Category</Label><Input placeholder="Delivery" /></div>
                  <div className="space-y-2"><Label>Language</Label><Input defaultValue="Bangla" /></div>
                </div>
                <Button className="w-full gradient-primary border-0">Save FAQ</Button>
              </div>
            </DialogContent>
          </Dialog>
        </>}
      />

      <Card className="p-5 mb-4 bg-primary/5 border-primary/20 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center"><Sparkles className="w-5 h-5 text-white" /></div>
        <div className="flex-1">
          <div className="font-semibold text-sm">AI knowledge is up to date</div>
          <div className="text-xs text-muted-foreground">Last indexed 3 minutes ago · {faqs.length} entries</div>
        </div>
        <Badge variant="outline" className="bg-success/10 text-success border-success/20">Active</Badge>
      </Card>

      <Card>
        <div className="p-4 border-b flex items-center gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input placeholder="Search FAQs..." className="pl-9 bg-muted/50 border-0" />
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
            {faqs.map((f) => (
              <TableRow key={f.id} className="hover:bg-muted/30">
                <TableCell>
                  <div className="font-medium font-bangla">{f.question}</div>
                  <div className="text-xs text-muted-foreground truncate max-w-md font-bangla mt-0.5">{f.answer}</div>
                </TableCell>
                <TableCell className="hidden md:table-cell"><Badge variant="outline">{f.category}</Badge></TableCell>
                <TableCell className="hidden md:table-cell"><Badge variant="secondary">{f.language}</Badge></TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="icon" className="w-8 h-8"><Edit2 className="w-3.5 h-3.5" /></Button>
                  <Button variant="ghost" size="icon" className="w-8 h-8 text-destructive"><Trash2 className="w-3.5 h-3.5" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
