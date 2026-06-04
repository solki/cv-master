import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import NavSidebar from "@/components/nav-sidebar";
import ErrorBoundary from "@/components/error-boundary";

export const metadata: Metadata = {
  title: "CV Master",
  description: "AI-powered resume generation from your career knowledge base",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta name="color-scheme" content="dark" />
      </head>
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        <Providers>
          <div className="flex min-h-screen">
            <NavSidebar />
            <ErrorBoundary>
              <main id="main-content" className="flex-1 p-6 max-w-5xl">{children}</main>
            </ErrorBoundary>
          </div>
        </Providers>
      </body>
    </html>
  );
}
