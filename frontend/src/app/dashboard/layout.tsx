"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { Eye, LayoutDashboard, Users, Image, FileText, Bell, LogOut, ChevronDown } from "lucide-react";
import { isLoggedIn, getUser, logout } from "@/lib/auth";
import { getBrands } from "@/lib/api";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/competitors", label: "Competitors", icon: Users },
  { href: "/dashboard/ads", label: "Creative Library", icon: Image },
  { href: "/dashboard/briefs", label: "Intel Briefs", icon: FileText },
  { href: "/dashboard/alerts", label: "Alerts", icon: Bell },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);
  const [brands, setBrands] = useState<any[]>([]);
  const [activeBrand, setActiveBrand] = useState<any>(null);

  useEffect(() => {
    if (!isLoggedIn()) { router.push("/login"); return; }
    setUser(getUser());
    getBrands().then(res => {
      setBrands(res.data);
      const stored = localStorage.getItem("vantage_brand_id");
      const found = res.data.find((b: any) => b.id === stored) || res.data[0];
      if (found) { setActiveBrand(found); localStorage.setItem("vantage_brand_id", found.id); }
    }).catch(() => router.push("/login"));
  }, []);

  const switchBrand = (brand: any) => {
    setActiveBrand(brand);
    localStorage.setItem("vantage_brand_id", brand.id);
    router.refresh();
  };

  return (
    <div className="flex h-screen bg-bg overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 border-r border-border flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-border flex items-center gap-2">
          <div className="w-7 h-7 bg-accent rounded-md flex items-center justify-center flex-shrink-0">
            <Eye size={13} className="text-white" />
          </div>
          <span className="font-bold text-base tracking-tight">Vantage</span>
        </div>

        {/* Brand selector */}
        {activeBrand && (
          <div className="px-3 py-3 border-b border-border">
            <p className="text-xs text-muted mb-1.5 uppercase tracking-wider">Active Brand</p>
            <div className="bg-card border border-border rounded-lg px-3 py-2 flex items-center justify-between">
              <span className="text-sm font-medium truncate">{activeBrand.name}</span>
              <ChevronDown size={13} className="text-muted flex-shrink-0" />
            </div>
          </div>
        )}

        {/* Nav */}
        <nav className="flex-1 py-3 px-2 space-y-0.5">
          {navItems.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link key={href} href={href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${active ? "bg-accent/10 text-accent" : "text-muted hover:text-white hover:bg-card"}`}>
                <Icon size={16} />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* User */}
        <div className="border-t border-border p-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-accent/20 rounded-full flex items-center justify-center text-accent text-xs font-bold flex-shrink-0">
              {user?.name?.[0]?.toUpperCase() || "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.name}</p>
              <p className="text-xs text-muted capitalize">{user?.subscription_tier}</p>
            </div>
            <button onClick={logout} className="text-muted hover:text-white transition-colors">
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
