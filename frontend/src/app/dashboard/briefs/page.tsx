"use client";
import { useEffect, useState } from "react";
import { getBriefs, getBrief, generateBrief } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import { FileText, Sparkles, ArrowLeft } from "lucide-react";

export default function BriefsPage() {
  const [briefs, setBriefs] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [brandId, setBrandId] = useState("");

  useEffect(() => {
    const id = localStorage.getItem("vantage_brand_id") || "";
    setBrandId(id);
    if (id) getBriefs(id).then(r => setBriefs(r.data)).finally(() => setLoading(false));
  }, []);

  const handleGenerate = async () => {
    if (!brandId) return;
    setGenerating(true);
    await generateBrief(brandId).catch(console.error);
    setTimeout(() => {
      getBriefs(brandId).then(r => setBriefs(r.data));
      setGenerating(false);
    }, 5000);
  };

  const openBrief = (b: any) => {
    getBrief(b.id).then(r => setSelected(r.data));
  };

  if (selected) return (
    <div className="p-8 max-w-3xl">
      <button onClick={() => setSelected(null)} className="flex items-center gap-2 text-muted hover:text-white text-sm mb-6 transition-colors">
        <ArrowLeft size={16} /> Back to all briefs
      </button>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Intelligence Brief</h1>
        <p className="text-muted text-sm mt-1">
          {new Date(selected.week_start).toLocaleDateString("en-IN", { month: "long", day: "numeric" })} — {new Date(selected.week_end).toLocaleDateString("en-IN", { month: "long", day: "numeric", year: "numeric" })}
        </p>
      </div>
      {selected.recommendations?.length > 0 && (
        <div className="bg-accent/5 border border-accent/20 rounded-xl p-5 mb-6">
          <p className="text-accent text-xs font-semibold uppercase tracking-wider mb-3">Strategic Recommendations</p>
          {selected.recommendations.map((r: string, i: number) => (
            <div key={i} className="flex items-start gap-3 mb-2 last:mb-0">
              <span className="text-accent font-bold text-sm flex-shrink-0">{i + 1}.</span>
              <p className="text-sm text-white">{r}</p>
            </div>
          ))}
        </div>
      )}
      <div className="bg-card border border-border rounded-xl p-6 prose max-w-none">
        <ReactMarkdown>{selected.content}</ReactMarkdown>
      </div>
    </div>
  );

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Intel Briefs</h1>
          <p className="text-muted text-sm mt-1">AI-generated weekly competitive intelligence</p>
        </div>
        <button onClick={handleGenerate} disabled={generating}
          className="bg-accent hover:bg-accent-dark disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors">
          <Sparkles size={15} />
          {generating ? "Generating..." : "Generate brief"}
        </button>
      </div>

      {loading ? <div className="text-muted text-sm">Loading...</div> : briefs.length === 0 ? (
        <div className="bg-card border border-dashed border-border rounded-xl p-12 text-center">
          <FileText size={32} className="text-muted mx-auto mb-4" />
          <p className="text-muted mb-4">No briefs yet. Generate your first intelligence brief.</p>
          <button onClick={handleGenerate} disabled={generating} className="text-accent hover:underline text-sm">
            {generating ? "Generating..." : "Generate now →"}
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {briefs.map(b => (
            <div key={b.id} onClick={() => openBrief(b)}
              className="bg-card border border-border rounded-xl p-5 cursor-pointer hover:border-accent/50 transition-all">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold mb-1">
                    Week of {new Date(b.week_start).toLocaleDateString("en-IN", { month: "short", day: "numeric" })} — {new Date(b.week_end).toLocaleDateString("en-IN", { month: "short", day: "numeric", year: "numeric" })}
                  </p>
                  {b.key_insights?.[0] && <p className="text-muted text-sm truncate">{b.key_insights[0]}</p>}
                </div>
                <span className="text-accent text-sm ml-4 flex-shrink-0">Read →</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
