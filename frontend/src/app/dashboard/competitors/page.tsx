"use client";
import { useEffect, useState } from "react";
import { Plus, RefreshCw, Trash2, Globe, X } from "lucide-react";
import { getCompetitors, addCompetitor, removeCompetitor, syncCompetitor } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

export default function CompetitorsPage() {
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [brandId, setBrandId] = useState<string>("");
  const [form, setForm] = useState({ name: "", website: "", facebook_page_id: "", instagram_handle: "" });

  useEffect(() => {
    const id = localStorage.getItem("vantage_brand_id") || "";
    setBrandId(id);
    if (id) fetchCompetitors(id);
  }, []);

  const fetchCompetitors = (id: string) => {
    getCompetitors(id).then(r => setCompetitors(r.data)).finally(() => setLoading(false));
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    await addCompetitor(brandId, form);
    setShowModal(false);
    setForm({ name: "", website: "", facebook_page_id: "", instagram_handle: "" });
    fetchCompetitors(brandId);
  };

  const handleSync = async (competitorId: string) => {
    setSyncing(competitorId);
    await syncCompetitor(brandId, competitorId).catch(console.error);
    setSyncing(null);
    fetchCompetitors(brandId);
  };

  const handleRemove = async (competitorId: string) => {
    if (!confirm("Remove this competitor?")) return;
    await removeCompetitor(brandId, competitorId);
    fetchCompetitors(brandId);
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Competitors</h1>
          <p className="text-muted text-sm mt-1">Brands you're tracking across Meta and Google</p>
        </div>
        <button onClick={() => setShowModal(true)}
          className="bg-accent hover:bg-accent-dark text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors">
          <Plus size={16} /> Add competitor
        </button>
      </div>

      {loading ? (
        <div className="text-muted text-sm">Loading...</div>
      ) : competitors.length === 0 ? (
        <div className="bg-card border border-dashed border-border rounded-xl p-12 text-center">
          <p className="text-muted mb-4">No competitors added yet.</p>
          <button onClick={() => setShowModal(true)} className="text-accent hover:underline text-sm">Add your first competitor →</button>
        </div>
      ) : (
        <div className="space-y-3">
          {competitors.map(c => (
            <div key={c.id} className="bg-card border border-border rounded-xl p-5 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center text-accent font-bold">
                  {c.name[0]}
                </div>
                <div>
                  <p className="font-medium">{c.name}</p>
                  <div className="flex items-center gap-3 mt-0.5">
                    {c.website && <a href={c.website} target="_blank" className="text-muted text-xs hover:text-accent flex items-center gap-1"><Globe size={11} /> {c.website.replace("https://", "")}</a>}
                    <span className="text-muted text-xs">{c.ad_count} ads tracked</span>
                    {c.last_synced_at && <span className="text-muted text-xs">Synced {formatDistanceToNow(new Date(c.last_synced_at), { addSuffix: true })}</span>}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => handleSync(c.id)} disabled={syncing === c.id}
                  className="text-muted hover:text-white border border-border hover:border-accent px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5 transition-colors">
                  <RefreshCw size={12} className={syncing === c.id ? "animate-spin" : ""} />
                  {syncing === c.id ? "Syncing..." : "Sync ads"}
                </button>
                <button onClick={() => handleRemove(c.id)} className="text-muted hover:text-red-400 p-1.5 transition-colors">
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
          <div className="bg-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-5">
              <h2 className="font-bold text-lg">Add competitor</h2>
              <button onClick={() => setShowModal(false)} className="text-muted hover:text-white"><X size={18} /></button>
            </div>
            <form onSubmit={handleAdd} className="space-y-4">
              {[
                { label: "Brand name *", key: "name", placeholder: "WOW Skin Science" },
                { label: "Website", key: "website", placeholder: "https://buywow.in" },
                { label: "Facebook Page ID", key: "facebook_page_id", placeholder: "123456789" },
                { label: "Instagram handle", key: "instagram_handle", placeholder: "@wowskinscienceofficial" },
              ].map(({ label, key, placeholder }) => (
                <div key={key}>
                  <label className="text-sm text-muted mb-1.5 block">{label}</label>
                  <input value={(form as any)[key]} onChange={e => setForm({ ...form, [key]: e.target.value })}
                    placeholder={placeholder}
                    className="w-full bg-bg border border-border rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-accent"
                    required={key === "name"} />
                </div>
              ))}
              <button type="submit" className="w-full bg-accent hover:bg-accent-dark text-white py-2.5 rounded-lg font-medium text-sm transition-colors">
                Add competitor
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
