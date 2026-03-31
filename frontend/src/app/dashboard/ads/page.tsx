"use client";
import { useEffect, useState } from "react";
import { getAds, getCompetitors } from "@/lib/api";
import { ExternalLink } from "lucide-react";

const spendConfig: Record<string, { label: string; className: string }> = {
  surge: { label: "Surge", className: "text-red-400 bg-red-400/10 border-red-400/20" },
  high: { label: "High", className: "text-orange-400 bg-orange-400/10 border-orange-400/20" },
  medium: { label: "Medium", className: "text-accent bg-accent/10 border-accent/20" },
  low: { label: "Low", className: "text-muted bg-muted/10 border-muted/20" },
};

const formatConfig: Record<string, string> = {
  video: "bg-purple-400/10 text-purple-400",
  carousel: "bg-emerald-400/10 text-emerald-400",
  image: "bg-blue-400/10 text-blue-400",
};

export default function AdsPage() {
  const [ads, setAds] = useState<any[]>([]);
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ competitor_id: "", platform: "", format: "", spend_signal: "" });
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    const id = localStorage.getItem("vantage_brand_id") || "";
    if (!id) return;
    getCompetitors(id).then(r => setCompetitors(r.data));
    fetchAds(id, filters);
  }, []);

  const fetchAds = (brandId: string, f: any) => {
    setLoading(true);
    const params = Object.fromEntries(Object.entries(f).filter(([_, v]) => v));
    getAds(brandId, params).then(r => { setAds(r.data.ads); setTotal(r.data.total); }).finally(() => setLoading(false));
  };

  const applyFilter = (key: string, value: string) => {
    const id = localStorage.getItem("vantage_brand_id") || "";
    const newF = { ...filters, [key]: value };
    setFilters(newF);
    fetchAds(id, newF);
  };

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Creative Library</h1>
        <p className="text-muted text-sm mt-1">{total} ads tracked across all competitors</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        {[
          { key: "competitor_id", placeholder: "All competitors", options: competitors.map(c => ({ value: c.id, label: c.name })) },
          { key: "platform", placeholder: "All platforms", options: [{ value: "meta", label: "Meta" }, { value: "google", label: "Google" }] },
          { key: "format", placeholder: "All formats", options: [{ value: "image", label: "Image" }, { value: "video", label: "Video" }, { value: "carousel", label: "Carousel" }] },
          { key: "spend_signal", placeholder: "All signals", options: [{ value: "surge", label: "Surge" }, { value: "high", label: "High" }, { value: "medium", label: "Medium" }, { value: "low", label: "Low" }] },
        ].map(({ key, placeholder, options }) => (
          <select key={key} value={(filters as any)[key]}
            onChange={e => applyFilter(key, e.target.value)}
            className="bg-card border border-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent">
            <option value="">{placeholder}</option>
            {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        ))}
      </div>

      {loading ? <div className="text-muted text-sm">Loading ads...</div> : ads.length === 0 ? (
        <div className="bg-card border border-dashed border-border rounded-xl p-12 text-center">
          <p className="text-muted">No ads found. Add competitors and sync to start tracking.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {ads.map(ad => {
            const spend = spendConfig[ad.spend_signal] || spendConfig.low;
            const fmt = formatConfig[ad.format] || formatConfig.image;
            return (
              <div key={ad.id} onClick={() => setSelected(ad)}
                className="bg-card border border-border rounded-xl p-5 cursor-pointer hover:border-accent/50 transition-all group">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs text-muted font-medium">{ad.competitor_name}</span>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${fmt} capitalize`}>{ad.format}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${spend.className} capitalize`}>{spend.label}</span>
                  </div>
                </div>
                {ad.headline && <p className="font-semibold text-sm mb-1.5 line-clamp-2">{ad.headline}</p>}
                {ad.body && <p className="text-muted text-xs line-clamp-3 mb-3">{ad.body}</p>}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-1.5 py-0.5 rounded capitalize ${ad.platform === "meta" ? "text-blue-400 bg-blue-400/10" : "text-green-400 bg-green-400/10"}`}>{ad.platform}</span>
                    {ad.cta && <span className="text-xs text-muted border border-border px-1.5 py-0.5 rounded">{ad.cta}</span>}
                  </div>
                  <span className="text-xs text-muted">{ad.first_seen ? new Date(ad.first_seen).toLocaleDateString("en-IN", { day: "numeric", month: "short" }) : ""}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Ad detail modal */}
      {selected && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4" onClick={() => setSelected(null)}>
          <div className="bg-card border border-border rounded-xl p-6 max-w-lg w-full" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold">Ad Detail</h2>
              <button onClick={() => setSelected(null)} className="text-muted hover:text-white text-xl">×</button>
            </div>
            <div className="space-y-3">
              <div><p className="text-xs text-muted mb-1">Competitor</p><p className="text-sm font-medium">{selected.competitor_name}</p></div>
              {selected.headline && <div><p className="text-xs text-muted mb-1">Headline</p><p className="text-sm">{selected.headline}</p></div>}
              {selected.body && <div><p className="text-xs text-muted mb-1">Body copy</p><p className="text-sm text-muted">{selected.body}</p></div>}
              {selected.cta && <div><p className="text-xs text-muted mb-1">CTA</p><p className="text-sm">{selected.cta}</p></div>}
              <div className="flex gap-4">
                <div><p className="text-xs text-muted mb-1">Platform</p><p className="text-sm capitalize">{selected.platform}</p></div>
                <div><p className="text-xs text-muted mb-1">Format</p><p className="text-sm capitalize">{selected.format}</p></div>
                <div><p className="text-xs text-muted mb-1">Spend signal</p><p className="text-sm capitalize">{selected.spend_signal}</p></div>
              </div>
              {selected.creative_url && (
                <a href={selected.creative_url} target="_blank" className="flex items-center gap-1 text-accent text-sm hover:underline">
                  <ExternalLink size={13} /> View creative
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
