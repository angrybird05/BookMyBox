import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  createRootRouteWithContext,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import type { ReactNode } from "react";

import appCss from "../styles.css?url";
import { AuthProvider } from "../context/AuthContext";
import { BookingProvider } from "../context/BookingContext";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Toasts from "../components/Toast";

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "BookMyBox — Book Box Cricket Grounds Instantly" },
      { name: "description", content: "Reserve box cricket slots in 60 seconds. Multi-slot booking, instant payment, no hidden fees." },
    ],
    links: [
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;800&family=Space+Mono:wght@400;700&display=swap" },
      { rel: "stylesheet", href: appCss },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: () => (
    <div style={{ minHeight: "70vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div className="neo-card text-center" style={{ maxWidth: 420 }}>
        <h1 style={{ fontSize: 64, fontWeight: 800 }}>404</h1>
        <p style={{ marginBottom: 16 }}>This page doesn't exist.</p>
        <a href="/" className="neo-btn">Go home</a>
      </div>
    </div>
  ),
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head><HeadContent /></head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BookingProvider>
          <Navbar />
          <Toasts />
          <main><Outlet /></main>
          <Footer />
        </BookingProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
