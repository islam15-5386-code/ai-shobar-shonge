import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { setAccessToken } from "@/lib/api";
import { toast } from "sonner";

export default function GoogleCallback() {
  const nav = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const access = params.get("access") || "";
    const refresh = params.get("refresh") || "";
    const error = params.get("error") || "";

    if (access && refresh) {
      setAccessToken(access);
      localStorage.setItem("refresh_token", refresh);
      toast.success("Google login successful");
      nav("/dashboard", { replace: true });
      return;
    }

    toast.error(error ? `Google login failed: ${error}` : "Google login failed");
    nav("/login", { replace: true });
  }, [nav]);

  return <div className="min-h-screen grid place-items-center text-sm text-muted-foreground">Completing Google sign in...</div>;
}
