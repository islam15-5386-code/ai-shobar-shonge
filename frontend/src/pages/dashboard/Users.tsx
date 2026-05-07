import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

type Me = {
  id: number;
  username: string;
  email: string;
  full_name: string;
  phone: string;
  role: string;
  is_active: boolean;
};

type TeamMember = {
  id: number;
  user_id: number;
  username: string;
  email: string;
  role: "owner" | "manager" | "agent";
};

export default function Users() {
  const [me, setMe] = useState<Me | null>(null);
  const [team, setTeam] = useState<TeamMember[]>([]);
  const [newUsername, setNewUsername] = useState("");
  const [newRole, setNewRole] = useState<"manager" | "agent">("agent");

  const load = async () => {
    try {
      const [meRes, teamRes] = await Promise.allSettled([
        apiFetch<Me>("/api/accounts/me/"),
        apiFetch<TeamMember[]>("/api/tenants/team-members/"),
      ]);
      if (meRes.status === "fulfilled") setMe(meRes.value);
      if (teamRes.status === "fulfilled") setTeam(teamRes.value);
    } catch {
      toast.error("Failed to load user dashboard");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const saveProfile = async () => {
    if (!me) return;
    try {
      await apiFetch("/api/accounts/me/", {
        method: "PATCH",
        body: JSON.stringify({ full_name: me.full_name, phone: me.phone }),
      });
      toast.success("Profile updated");
    } catch {
      toast.error("Profile update failed");
    }
  };

  const addTeam = async () => {
    if (!newUsername.trim()) return;
    try {
      const res = await apiFetch<{ auto_created_user?: boolean }>("/api/tenants/team-members/", {
        method: "POST",
        body: JSON.stringify({ username: newUsername.trim(), role: newRole }),
      });
      toast.success(res?.auto_created_user ? "Team member added (new user created)" : "Team member added");
      setNewUsername("");
      await load();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Add team member failed";
      toast.error(message);
    }
  };

  const updateRole = async (memberId: number, role: "owner" | "manager" | "agent") => {
    try {
      await apiFetch("/api/tenants/team-members/", {
        method: "PATCH",
        body: JSON.stringify({ member_id: memberId, role }),
      });
      toast.success("Role updated");
      await load();
    } catch {
      toast.error("Role update failed");
    }
  };

  const removeMember = async (memberId: number) => {
    try {
      await apiFetch("/api/tenants/team-members/", {
        method: "DELETE",
        body: JSON.stringify({ member_id: memberId }),
      });
      toast.success("Member deactivated");
      await load();
    } catch {
      toast.error("Member remove failed");
    }
  };

  return (
    <div className="p-4 md:p-8 space-y-6">
      <PageHeader title="User Dashboard" subtitle="Manage your profile and team members (Admin/Owner/Manager)" />

      <Card className="p-5 space-y-3">
        <h3 className="font-semibold">My Profile</h3>
        <div className="grid md:grid-cols-2 gap-3">
          <div className="space-y-1">
            <Label>Full name</Label>
            <Input value={me?.full_name || ""} onChange={(e) => setMe((p) => (p ? { ...p, full_name: e.target.value } : p))} />
          </div>
          <div className="space-y-1">
            <Label>Phone</Label>
            <Input value={me?.phone || ""} onChange={(e) => setMe((p) => (p ? { ...p, phone: e.target.value } : p))} />
          </div>
        </div>
        <div className="text-sm text-muted-foreground">Username: {me?.username || "-"} · Email: {me?.email || "-"} · Role: {me?.role || "-"}</div>
        <Button onClick={saveProfile}>Save Profile</Button>
      </Card>

      <Card className="p-5 space-y-4">
        <h3 className="font-semibold">Team Management</h3>
        <div className="flex flex-wrap gap-2">
          <Input className="max-w-xs" placeholder="username or email to add" value={newUsername} onChange={(e) => setNewUsername(e.target.value)} />
          <select className="h-10 rounded-md border px-3" value={newRole} onChange={(e) => setNewRole(e.target.value as "manager" | "agent")}>
            <option value="agent">agent</option>
            <option value="manager">manager</option>
          </select>
          <Button onClick={addTeam}>Add Member</Button>
        </div>

        <div className="space-y-2">
          {team.map((m) => (
            <div key={m.id} className="border rounded-md p-3 flex flex-wrap items-center gap-2 justify-between">
              <div className="text-sm">
                <div className="font-medium">{m.username}</div>
                <div className="text-muted-foreground">{m.email}</div>
              </div>
              <div className="flex items-center gap-2">
                <select className="h-9 rounded-md border px-2" value={m.role} onChange={(e) => updateRole(m.id, e.target.value as "owner" | "manager" | "agent")}>
                  <option value="owner">owner</option>
                  <option value="manager">manager</option>
                  <option value="agent">agent</option>
                </select>
                <Button variant="outline" onClick={() => removeMember(m.id)}>Deactivate</Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
