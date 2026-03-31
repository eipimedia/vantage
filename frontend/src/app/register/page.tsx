"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye } from "lucide-react";
import { register } from "@/lib/api";
import { createBrand } from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [brandName, setBrandName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await register(name, email, password);
      setToken(res.data.token, res.data.user);
      // Create their first brand
      if (brandName) {
        const brandRes = await createBrand({ name: brandName });
        localStorage.setItem("vantage_brand_id", brandRes.data.id);
      }
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
            <Eye size={16} className="text-white" />
          </div>
          <span className="font-bold text-xl">Vantage</span>
        </div>
        <div className="bg-card border border-border rounded-xl p-8">
          <h1 className="text-2xl font-bold mb-2">Get started</h1>
          <p className="text-muted text-sm mb-6">Create your competitive intelligence workspace</p>
          {error && <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm px-4 py-3 rounded-lg mb-4">{error}</div>}
          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="text-sm text-muted mb-1.5 block">Your name</label>
              <input value={name} onChange={e => setName(e.target.value)}
                className="w-full bg-bg border border-border rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-accent"
                placeholder="Rohit Reddy" required />
            </div>
            <div>
              <label className="text-sm text-muted mb-1.5 block">Your brand name</label>
              <input value={brandName} onChange={e => setBrandName(e.target.value)}
                className="w-full bg-bg border border-border rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-accent"
                placeholder="Mamaearth" required />
            </div>
            <div>
              <label className="text-sm text-muted mb-1.5 block">Work email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                className="w-full bg-bg border border-border rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-accent"
                placeholder="you@brand.com" required />
            </div>
            <div>
              <label className="text-sm text-muted mb-1.5 block">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                className="w-full bg-bg border border-border rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-accent"
                placeholder="••••••••" minLength={6} required />
            </div>
            <button type="submit" disabled={loading}
              className="w-full bg-accent hover:bg-accent-dark disabled:opacity-50 text-white py-3 rounded-lg font-medium transition-colors">
              {loading ? "Creating account..." : "Create account"}
            </button>
          </form>
          <p className="text-center text-muted text-sm mt-6">
            Already have an account? <Link href="/login" className="text-accent hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
