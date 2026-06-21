import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from "react-router-dom";
import { Toaster } from "sonner";
import "@/App.css";
import { CartProvider } from "./context/CartContext";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Splash from "./pages/Splash";
import Home from "./pages/Home";
import CoreDivision from "./pages/CoreDivision";
import LegacyDivision from "./pages/LegacyDivision";
import ProductDetail from "./pages/ProductDetail";
import CampaignList from "./pages/CampaignList";
import CampaignDetail from "./pages/CampaignDetail";
import Logbook from "./pages/Logbook";
import Contact from "./pages/Contact";
import FAQ from "./pages/FAQ";
import LegalPage from "./pages/LegalPage";
import AdminLogin from "./pages/admin/AdminLogin";
import AdminDashboard from "./pages/admin/AdminDashboard";

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}

// admin.strengthinorder.com points at the same app/service; send its root straight to the dashboard.
function AdminHostRedirect() {
  const location = useLocation();
  const navigate = useNavigate();
  useEffect(() => {
    if (window.location.hostname.startsWith("admin.") && location.pathname === "/") {
      navigate("/admin", { replace: true });
    }
  }, [location.pathname, navigate]);
  return null;
}

function Chrome({ children }) {
  const location = useLocation();
  const isSplash = location.pathname === "/";
  const isAdmin = location.pathname.startsWith("/admin");
  return (
    <>
      {!isSplash && !isAdmin && <Header />}
      <main>{children}</main>
      {!isSplash && !isAdmin && <Footer />}
    </>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <CartProvider>
          <ScrollToTop />
          <AdminHostRedirect />
          <Chrome>
            <Routes>
              <Route path="/" element={<Splash />} />
              <Route path="/home" element={<Home />} />
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/core" element={<CoreDivision />} />
              <Route path="/legacy" element={<LegacyDivision />} />
              <Route path="/product/:slug" element={<ProductDetail />} />
              <Route path="/campaigns" element={<CampaignList />} />
              <Route path="/campaigns/:slug" element={<CampaignDetail />} />
              <Route path="/logbook" element={<Logbook />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/faq" element={<FAQ />} />
              <Route path="/privacy" element={<LegalPage />} />
              <Route path="/terms" element={<LegalPage />} />
              <Route path="/returns" element={<LegalPage />} />
              <Route path="/shipping" element={<LegalPage />} />
              <Route path="/accessibility" element={<LegalPage />} />
            </Routes>
          </Chrome>
          <Toaster
            theme="dark"
            position="top-right"
            toastOptions={{
              style: {
                background: "#11141C",
                border: "1px solid #2A3040",
                borderRadius: 0,
                color: "#fff",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "12px",
                letterSpacing: "0.05em",
              },
            }}
          />
        </CartProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
