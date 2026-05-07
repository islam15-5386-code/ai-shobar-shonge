import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ForgotPassword from "./pages/auth/ForgotPassword";
import DashboardLayout from "./components/dashboard/DashboardLayout";
import Overview from "./pages/dashboard/Overview";
import Inbox from "./pages/dashboard/Inbox";
import Tickets from "./pages/dashboard/Tickets";
import FAQs from "./pages/dashboard/FAQs";
import Products from "./pages/dashboard/Products";
import Integrations from "./pages/dashboard/Integrations";
import AISettings from "./pages/dashboard/AISettings";
import History from "./pages/dashboard/History";
import Billing from "./pages/dashboard/Billing";
import Onboarding from "./pages/dashboard/Onboarding";
import Users from "./pages/dashboard/Users";
import VendorsPage from "./pages/marketplace/VendorsPage";
import VendorDetailPage from "./pages/marketplace/VendorDetailPage";
import MarketplaceOrdersPage from "./pages/marketplace/MarketplaceOrdersPage";
import MarketplaceOrderDetailPage from "./pages/marketplace/MarketplaceOrderDetailPage";
import CommissionsPage from "./pages/marketplace/CommissionsPage";
import PayoutsPage from "./pages/marketplace/PayoutsPage";
import CategoriesPage from "./pages/marketplace/CategoriesPage";
import MarketplaceSettingsPage from "./pages/marketplace/MarketplaceSettingsPage";
import VendorDashboardPage from "./pages/vendor/VendorDashboardPage";
import VendorProductsPage from "./pages/vendor/VendorProductsPage";
import VendorOrdersPage from "./pages/vendor/VendorOrdersPage";
import VendorTicketsPage from "./pages/vendor/VendorTicketsPage";
import VendorPayoutsPage from "./pages/vendor/VendorPayoutsPage";
import VendorFaqsPage from "./pages/vendor/VendorFaqsPage";
import VendorSettingsPage from "./pages/vendor/VendorSettingsPage";

const queryClient = new QueryClient();

function RequireAuth({ children }: { children: JSX.Element }) {
  const token = localStorage.getItem("access_token");
  const location = useLocation();
  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return children;
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route
            path="/dashboard/onboarding"
            element={
              <RequireAuth>
                <Onboarding />
              </RequireAuth>
            }
          />
          <Route
            path="/dashboard"
            element={
              <RequireAuth>
                <DashboardLayout />
              </RequireAuth>
            }
          >
            <Route index element={<Overview />} />
            <Route path="inbox" element={<Inbox />} />
            <Route path="tickets" element={<Tickets />} />
            <Route path="faqs" element={<FAQs />} />
            <Route path="products" element={<Products />} />
            <Route path="integrations" element={<Integrations />} />
            <Route path="ai-settings" element={<AISettings />} />
            <Route path="history" element={<History />} />
            <Route path="billing" element={<Billing />} />
            <Route path="users" element={<Users />} />
            <Route path="vendors" element={<VendorsPage />} />
            <Route path="vendors/:id" element={<VendorDetailPage />} />
            <Route path="orders" element={<MarketplaceOrdersPage />} />
            <Route path="orders/:id" element={<MarketplaceOrderDetailPage />} />
            <Route path="commissions" element={<CommissionsPage />} />
            <Route path="payouts" element={<PayoutsPage />} />
            <Route path="categories" element={<CategoriesPage />} />
            <Route path="marketplace-settings" element={<MarketplaceSettingsPage />} />
          </Route>
          <Route
            path="/vendor/dashboard"
            element={
              <RequireAuth>
                <VendorDashboardPage />
              </RequireAuth>
            }
          />
          <Route
            path="/vendor/products"
            element={
              <RequireAuth>
                <VendorProductsPage />
              </RequireAuth>
            }
          />
          <Route
            path="/vendor/orders"
            element={
              <RequireAuth>
                <VendorOrdersPage />
              </RequireAuth>
            }
          />
          <Route
            path="/vendor/tickets"
            element={
              <RequireAuth>
                <VendorTicketsPage />
              </RequireAuth>
            }
          />
          <Route
            path="/vendor/payouts"
            element={
              <RequireAuth>
                <VendorPayoutsPage />
              </RequireAuth>
            }
          />
          <Route
            path="/vendor/faqs"
            element={
              <RequireAuth>
                <VendorFaqsPage />
              </RequireAuth>
            }
          />
          <Route
            path="/vendor/settings"
            element={
              <RequireAuth>
                <VendorSettingsPage />
              </RequireAuth>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
