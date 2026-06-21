import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock } from "lucide-react";
import { toast } from "sonner";
import Logo from "../../components/Logo";
import { adminLogin, getAdminToken } from "../../lib/adminApi";

export default function AdminLogin() {
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  if (getAdminToken()) {
    navigate("/admin", { replace: true });
  }

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await adminLogin(password);
      navigate("/admin", { replace: true });
    } catch {
      toast.error("Incorrect password.");
    }
    setLoading(false);
  };

  return (
    <div
      data-testid="admin-login-page"
      className="min-h-screen bg-[#06080C] text-white flex items-center justify-center px-5"
    >
      <form
        onSubmit={submit}
        className="w-full max-w-sm border border-[#1F2330] bg-[#0A0D14] p-8"
      >
        <div className="flex flex-col items-center mb-8">
          <Logo className="w-14 h-14 mb-3" />
          <div className="font-display text-2xl etched-steel">AEGIS ADMIN</div>
          <div className="label mt-1 text-[#6E7585]">Authorized Access Only</div>
        </div>

        <label className="label text-[#D4AF37] block mb-2">Password</label>
        <div className="flex items-center gap-2 bg-[#06080C] border border-[#1F2330] focus-within:border-[#D4AF37] px-4 py-3 mb-6">
          <Lock className="w-4 h-4 text-[#6E7585]" />
          <input
            data-testid="admin-password-input"
            type="password"
            required
            autoFocus
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="flex-1 bg-transparent outline-none font-mono text-sm tracking-wider"
            placeholder="••••••••"
          />
        </div>

        <button
          data-testid="admin-login-submit"
          disabled={loading}
          className="w-full bg-[#D4AF37] hover:bg-[#E6C454] disabled:opacity-60 px-5 py-3 font-mono uppercase tracking-widest text-[11px] font-bold text-black"
        >
          {loading ? "Verifying..." : "Enter"}
        </button>
      </form>
    </div>
  );
}
