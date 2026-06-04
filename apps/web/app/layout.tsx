import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import NavSidebar from "@/components/nav-sidebar";

export const metadata: Metadata = {
  title: "CV Master",
  description: "AI-powered resume generation from your career knowledge base",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-zinc-50 text-zinc-900">
        <Providers>
          <div className="flex min-h-screen">
            <NavSidebar />
            <main className="flex-1 p-6 max-w-7xl">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
