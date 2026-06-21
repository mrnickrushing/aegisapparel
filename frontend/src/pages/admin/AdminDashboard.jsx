import React, { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { LogOut, Mail, Send, Users, MessageSquare } from "lucide-react";
import { toast } from "sonner";
import Logo from "../../components/Logo";
import {
  clearAdminToken,
  fetchContactMessages,
  fetchSubscribers,
  getAdminToken,
  sendNewsletterBlast,
} from "../../lib/adminApi";

function StatCard({ icon: Icon, label, value }) {
  return (
    <div className="bg-[#0A0D14] border border-[#1F2330] p-6 flex items-center gap-4">
      <Icon className="w-6 h-6 text-[#D4AF37]" />
      <div>
        <div className="font-display text-3xl text-white">{value}</div>
        <div className="label text-[#6E7585]">{label}</div>
      </div>
    </div>
  );
}

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [subscribers, setSubscribers] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [sending, setSending] = useState(false);

  const handleAuthError = useCallback(
    (err) => {
      if (err?.response?.status === 401) {
        clearAdminToken();
        navigate("/admin/login", { replace: true });
        return true;
      }
      return false;
    },
    [navigate]
  );

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [subRes, msgRes] = await Promise.all([fetchSubscribers(), fetchContactMessages()]);
      setSubscribers(subRes.subscribers);
      setMessages(msgRes.messages);
    } catch (err) {
      if (!handleAuthError(err)) toast.error("Could not load admin data.");
    }
    setLoading(false);
  }, [handleAuthError]);

  useEffect(() => {
    if (!getAdminToken()) {
      navigate("/admin/login", { replace: true });
      return;
    }
    loadData();
  }, [navigate, loadData]);

  const logout = () => {
    clearAdminToken();
    navigate("/admin/login", { replace: true });
  };

  const submitBlast = async (e) => {
    e.preventDefault();
    if (!subject.trim() || !body.trim()) return;
    if (
      !window.confirm(
        `Send this newsletter to ${subscribers.length} subscriber(s)? This cannot be undone.`
      )
    ) {
      return;
    }
    setSending(true);
    try {
      const res = await sendNewsletterBlast(subject, body);
      toast.success(`Sent to ${res.sent} subscriber(s).${res.failed ? ` ${res.failed} failed.` : ""}`);
      setSubject("");
      setBody("");
    } catch (err) {
      if (!handleAuthError(err)) toast.error("Could not send newsletter.");
    }
    setSending(false);
  };

  return (
    <div data-testid="admin-dashboard-page" className="min-h-screen bg-[#06080C] text-white">
      <header className="border-b border-[#1F2330] bg-[#06080C]/95 backdrop-blur-xl sticky top-0 z-10">
        <div className="px-5 md:px-10 h-[76px] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Logo className="w-10 h-10" />
            <div className="leading-none">
              <div className="font-display text-xl etched-steel">AEGIS ADMIN</div>
              <div className="label text-[#6E7585] mt-0.5">Strength in Order</div>
            </div>
          </div>
          <button
            data-testid="admin-logout-btn"
            onClick={logout}
            className="flex items-center gap-2 border border-[#1F2330] hover:border-[#D4AF37] px-4 py-2.5 font-mono uppercase tracking-widest text-[11px] text-[#A0A6B5] hover:text-[#D4AF37] transition-colors"
          >
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </header>

      <main className="px-5 md:px-10 py-10 max-w-6xl mx-auto space-y-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-px bg-[#1F2330]">
          <StatCard icon={Users} label="Newsletter Subscribers" value={subscribers.length} />
          <StatCard icon={MessageSquare} label="Contact Messages" value={messages.length} />
        </div>

        <section data-testid="admin-blast-section" className="bg-[#0A0D14] border border-[#1F2330] p-6 md:p-8">
          <div className="label text-[#D4AF37] mb-4">Send Newsletter to All Subscribers</div>
          <form onSubmit={submitBlast} className="space-y-4">
            <input
              data-testid="admin-blast-subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              required
              placeholder="SUBJECT LINE"
              className="w-full bg-[#06080C] border border-[#1F2330] focus:border-[#D4AF37] outline-none px-4 py-3 font-mono text-sm tracking-wider uppercase placeholder:text-[#6E7585]"
            />
            <textarea
              data-testid="admin-blast-body"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              required
              rows={6}
              placeholder="Message body..."
              className="w-full bg-[#06080C] border border-[#1F2330] focus:border-[#D4AF37] outline-none px-4 py-3 font-mono text-sm leading-relaxed placeholder:text-[#6E7585]"
            />
            <button
              data-testid="admin-blast-submit"
              disabled={sending || subscribers.length === 0}
              className="flex items-center gap-2 bg-[#D4AF37] hover:bg-[#E6C454] disabled:opacity-60 px-5 py-3 font-mono uppercase tracking-widest text-[11px] font-bold text-black"
            >
              {sending ? "Sending..." : (
                <>
                  Send to {subscribers.length} Subscribers <Send className="w-3 h-3" />
                </>
              )}
            </button>
          </form>
        </section>

        <section data-testid="admin-subscribers-section">
          <div className="label text-[#D4AF37] mb-4">Newsletter Subscribers</div>
          <div className="border border-[#1F2330] max-h-[420px] overflow-y-auto">
            {loading ? (
              <div className="p-6 text-[#6E7585] text-sm">Loading...</div>
            ) : subscribers.length === 0 ? (
              <div className="p-6 text-[#6E7585] text-sm">No subscribers yet.</div>
            ) : (
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-[#0A0D14]">
                  <tr className="text-left label text-[#6E7585] border-b border-[#1F2330]">
                    <th className="px-4 py-3 font-normal">Email</th>
                    <th className="px-4 py-3 font-normal">Signed Up</th>
                  </tr>
                </thead>
                <tbody>
                  {subscribers.map((s) => (
                    <tr key={s.id} className="border-b border-[#1F2330]/60">
                      <td className="px-4 py-3 flex items-center gap-2">
                        <Mail className="w-3.5 h-3.5 text-[#6E7585]" />
                        {s.email}
                      </td>
                      <td className="px-4 py-3 text-[#A0A6B5] font-mono text-xs">
                        {new Date(s.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>

        <section data-testid="admin-contacts-section">
          <div className="label text-[#D4AF37] mb-4">Contact Form Messages</div>
          <div className="border border-[#1F2330] divide-y divide-[#1F2330]/60 max-h-[480px] overflow-y-auto">
            {loading ? (
              <div className="p-6 text-[#6E7585] text-sm">Loading...</div>
            ) : messages.length === 0 ? (
              <div className="p-6 text-[#6E7585] text-sm">No messages yet.</div>
            ) : (
              messages.map((m) => (
                <div key={m.id} className="p-4">
                  <div className="flex justify-between items-baseline gap-3 mb-1">
                    <div className="text-white text-sm font-medium">{m.full_name}</div>
                    <div className="text-[#6E7585] font-mono text-[10px]">
                      {new Date(m.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div className="text-[#A0A6B5] text-xs mb-2">
                    {m.email}
                    {m.subject ? ` · ${m.subject}` : ""}
                  </div>
                  <p className="text-[#A0A6B5] text-sm leading-relaxed">{m.message}</p>
                </div>
              ))
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
