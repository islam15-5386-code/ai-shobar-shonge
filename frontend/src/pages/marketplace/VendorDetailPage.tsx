import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/dashboard/PageHeader";

export default function VendorDetailPage() {
  return <div className="p-4 md:p-8"><PageHeader title="Vendor Details" subtitle="Detailed vendor view" /><Card className="p-4 text-sm text-muted-foreground">Use /api/vendors/{id}/ for detailed data binding in next iteration.</Card></div>;
}
