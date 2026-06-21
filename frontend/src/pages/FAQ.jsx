import React from "react";
import { Link } from "react-router-dom";
import { ChevronRight, ShieldCheck } from "lucide-react";
import { faqItems } from "../content/storefrontContent";

export default function FAQ() {
  return (
    <div className="bg-[#06080C] text-white min-h-screen">
      <section className="border-b border-[#1F2330] relative overflow-hidden">
        <div className="absolute inset-0 dusky-sky opacity-40" />
        <div className="absolute inset-0 warning-stripes opacity-10" />
        <div className="relative max-w-6xl mx-auto px-5 md:px-10 py-16 md:py-20">
          <div className="label mb-3 text-[#D4AF37]">/ Support Briefing</div>
          <h1 className="font-display text-5xl sm:text-7xl uppercase tracking-[0.05em] etched leading-none">
            FAQ
          </h1>
          <p className="text-[#A0A6B5] mt-4 max-w-3xl">
            Clear answers for shipping, returns, sizing, Legacy access, and the
            parts of the storefront people ask about most.
          </p>
          <div className="mt-6 inline-flex items-center gap-2 border border-[#2A3040] bg-[#11141C] px-3 py-2 font-mono text-[10px] uppercase tracking-[0.25em] text-[#A0A6B5]">
            <ShieldCheck className="w-3 h-3 text-[#D4AF37]" />
            Support {`support@rushingtechnologies.com`}
          </div>
        </div>
      </section>

      <section className="max-w-4xl mx-auto px-5 md:px-10 py-14 space-y-4">
        {faqItems.map((item) => (
          <details key={item.question} className="group border border-[#1F2330] bg-[#0A0D14] corners p-5 md:p-6">
            <summary className="cursor-pointer list-none flex items-center justify-between gap-4 font-display text-xl uppercase tracking-[0.05em]">
              <span>{item.question}</span>
              <ChevronRight className="w-4 h-4 text-[#D4AF37] transition-transform group-open:rotate-90" />
            </summary>
            <p className="mt-4 text-[#A0A6B5] leading-relaxed max-w-3xl">{item.answer}</p>
          </details>
        ))}

        <div className="pt-4 flex flex-wrap gap-3">
          <Link
            to="/contact"
            className="inline-flex items-center gap-2 border border-[#D4AF37] hover:bg-[#D4AF37] hover:text-black text-[#D4AF37] px-5 py-3 font-mono uppercase tracking-[0.3em] text-[11px] transition-colors"
          >
            Contact Support
          </Link>
          <Link
            to="/shipping"
            className="inline-flex items-center gap-2 border border-[#1F2330] hover:border-white text-[#A0A6B5] hover:text-white px-5 py-3 font-mono uppercase tracking-[0.3em] text-[11px] transition-colors"
          >
            Shipping Policy
          </Link>
        </div>
      </section>
    </div>
  );
}
