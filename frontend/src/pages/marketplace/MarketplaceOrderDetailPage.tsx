import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/dashboard/PageHeader";

export default function MarketplaceOrderDetailPage() {
  return <div className="p-4 md:p-8"><PageHeader title="Order Details" subtitle="Marketplace order details" /><Card className="p-4 text-sm text-muted-foreground">Use /api/marketplace/orders/{id}/ for detailed binding.</Card></div>;
}
