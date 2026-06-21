import React from "react";
import { Link, useLocation, Navigate } from "react-router-dom";
import { ShieldCheck } from "lucide-react";
import { legalPages } from "../content/storefrontContent";

const routeToKey = {
  privacy: "privacy",
  terms: "terms",
  returns: "returns",
  shipping: "shipping",
  accessibility: "accessibility",
};

export default function LegalPage() {
  const { pathname } = useLocation();
  const slug = pathname.replace(/^\//, "");
  const key = routeToKey[slug];
  const page = key ? legalPages[key] : null;

  if (!page) {
    return <Navigate to="/privacy" replace />;
  }

  return (
    <div className="bg-[#06080C] text-white min-h-screen">
      <section className="border-b border-[#1F2330] relative overflow-hidden">
        <div className="absolute inset-0 warning-stripes opacity-15" />
        <div className="relative max-w-5xl mx-auto px-5 md:px-10 py-16 md:py-20">
          <div className="label mb-3 text-[#D4AF37]">/ Policy File</div>
          <h1 className="font-display text-5xl sm:text-7xl uppercase tracking-[0.05em] etched leading-none">
            {page.title}
          </h1>
          <p className="text-[#A0A6B5] mt-4 max-w-3xl">{page.intro}</p>
          <div className="mt-6 inline-flex items-center gap-2 border border-[#2A3040] bg-[#11141C] px-3 py-2 font-mono text-[10px] uppercase tracking-[0.25em] text-[#A0A6B5]">
            <ShieldCheck className="w-3 h-3 text-[#D4AF37]" />
            Effective {page.effectiveDate} · Support {page.supportEmail}
          </div>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-5 md:px-10 py-14 space-y-6">
        {page.sections.map((section) => (
          <article key={section.title} className="border border-[#1F2330] bg-[#0A0D14] corners p-6 md:p-8">
            <div className="label mb-3 text-[#D4AF37]">/ {section.title}</div>
            <p className="text-[#A0A6B5] leading-relaxed">{section.body}</p>
          </article>
        ))}

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <Link
            to="/contact"
            className="inline-flex items-center gap-2 border border-[#D4AF37] hover:bg-[#D4AF37] hover:text-black text-[#D4AF37] px-5 py-3 font-mono uppercase tracking-[0.3em] text-[11px] transition-colors"
          >
            Contact Support
          </Link>
          <a
            href={`mailto:${page.supportEmail}`}
            className="inline-flex items-center gap-2 border border-[#1F2330] hover:border-white text-[#A0A6B5] hover:text-white px-5 py-3 font-mono uppercase tracking-[0.3em] text-[11px] transition-colors"
          >
            {page.supportEmail}
          </a>
        </div>
      </section>
    </div>
  );
}
