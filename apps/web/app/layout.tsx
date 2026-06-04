import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "CV Master",
  description: "AI-powered resume generation from your career knowledge base",
};

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "□" },
  { href: "/profile", label: "Career Profile", icon: "▣" },
  { href: "/projects", label: "Projects", icon: "≣" },
  { href: "/evidence", label: "Evidence", icon: "◎" },
  { href: "/jd", label: "JD Analyzer", icon: "▽" },
  { href: "/resumes", label: "Resume Generator", icon: "◇" },
  { href: "/library", label: "Resume Library", icon: "◫" },
  { href: "/vault", label: "Vault", icon: "▤" },
  { href: "/settings", label: "Settings", icon: "⚙" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-zinc-50 text-zinc-900">
        <Providers>
          <div className="flex min-h-screen">
            <nav className="w-56 bg-white border-r border-zinc-200 flex-shrink-0 hidden md:flex flex-col">
              <div className="p-4 font-bold text-lg border-b border-zinc-100">CV Master</div>
              <div className="flex-1 py-2">
                {NAV_ITEMS.map((item) => (
                  <a
                    key={item.href}
                    href={item.href}
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 transition-colors"
                  >
                    <span className="text-zinc-400">{item.icon}</span>
                    {item.label}
                  </a>
                ))}
              </div>
            </nav>
            <main className="flex-1 p-6 max-w-7xl">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
