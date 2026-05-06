import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
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

const queryClient = new QueryClient();

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
          <Route path="/dashboard/onboarding" element={<Onboarding />} />
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<Overview />} />
            <Route path="inbox" element={<Inbox />} />
            <Route path="tickets" element={<Tickets />} />
            <Route path="faqs" element={<FAQs />} />
            <Route path="products" element={<Products />} />
            <Route path="integrations" element={<Integrations />} />
            <Route path="ai-settings" element={<AISettings />} />
            <Route path="history" element={<History />} />
            <Route path="billing" element={<Billing />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
