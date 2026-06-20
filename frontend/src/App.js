import React from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
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

function Chrome({ children }) {
  const location = useLocation();
  const isSplash = location.pathname === "/";
  return (
    <>
      {!isSplash && <Header />}
      <main>{children}</main>
      {!isSplash && <Footer />}
    </>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <CartProvider>
          <Chrome>
            <Routes>
              <Route path="/" element={<Splash />} />
              <Route path="/home" element={<Home />} />
              <Route path="/core" element={<CoreDivision />} />
              <Route path="/legacy" element={<LegacyDivision />} />
              <Route path="/product/:slug" element={<ProductDetail />} />
              <Route path="/campaigns" element={<CampaignList />} />
              <Route path="/campaigns/:slug" element={<CampaignDetail />} />
              <Route path="/logbook" element={<Logbook />} />
              <Route path="/contact" element={<Contact />} />
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
