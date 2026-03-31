"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye } from "lucide-react";
import { login } from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("demo@getvantage.io");
  const [password, setPassword] = useState("demo123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await login(email, password);
      setToken(res.data.token, res.data.user);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed. Check your credentials.");
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
          <h1 className="text-2xl font-bold mb-2">Welcome back</h1>
          <p className="text-muted text-sm mb-6">Sign in to your intelligence dashboard</p>
          {error && <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm px-4 py-3 rounded-lg mb-4">{error}</div>}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-sm text-muted mb-1.5 block">Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                className="w-full bg-bg border border-border rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-accent transition-colors"
                placeholder="you@brand.com" required />
            </div>
            <div>
              <label className="text-sm text-muted mb-1.5 block">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                className="w-full bg-bg border border-border rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-accent transition-colors"
                placeholder="••••••••" required />
            </div>
            <button type="submit" disabled={loading}
              className="w-full bg-accent hover:bg-accent-dark disabled:opacity-50 text-white py-3 rounded-lg font-medium transition-colors">
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>
          <p className="text-center text-muted text-sm mt-6">
            No account? <Link href="/register" className="text-accent hover:underline">Get started free</Link>
          </p>
          <p className="text-center text-muted text-xs mt-3">Demo: demo@getvantage.io / demo123</p>
        </div>
      </div>
    </div>
  );
}
