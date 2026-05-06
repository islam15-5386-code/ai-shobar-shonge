import { Link, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-[#f6f8fb] flex items-center justify-center px-4">
      <div className="max-w-xl w-full rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-md">
        <h1 className="mb-2 text-6xl font-black text-primary">404</h1>
        <p className="mb-2 text-2xl font-bold">Page not found</p>
        <p className="mb-6 text-muted-foreground">The page you requested does not exist or was moved.</p>
        <div className="flex items-center justify-center gap-2">
          <Link to="/"><Button variant="outline">Go Home</Button></Link>
          <Link to="/dashboard"><Button className="bg-primary hover:bg-primary/90">Open Dashboard</Button></Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
