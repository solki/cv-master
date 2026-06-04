"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useStore } from "@/lib/store";

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

export default function NavSidebar() {
  const pathname = usePathname();
  const sidebarOpen = useStore((s) => s.sidebarOpen);
  const toggleSidebar = useStore((s) => s.toggleSidebar);
  const setSidebarOpen = useStore((s) => s.setSidebarOpen);

  return (
    <>
      {/* Mobile hamburger button */}
      <button
        onClick={toggleSidebar}
        className="md:hidden fixed top-3 left-3 z-50 p-2 rounded-md bg-white border border-zinc-200 shadow-sm hover:bg-zinc-50 transition-colors"
        aria-label="Toggle navigation"
      >
        <svg className="w-5 h-5 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {sidebarOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/30 z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <nav
        className={`w-56 bg-white border-r border-zinc-200 flex-shrink-0 flex-col z-40
          fixed inset-y-0 left-0 transition-transform duration-200 md:relative md:flex
          ${sidebarOpen ? "translate-x-0 flex" : "-translate-x-full md:translate-x-0 md:flex"}`}
      >
        <div className="p-4 font-bold text-lg border-b border-zinc-100">
          CV Master
        </div>
        <div className="flex-1 py-2 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                  isActive
                    ? "bg-blue-50 text-blue-700 font-medium border-r-2 border-blue-600"
                    : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900"
                }`}
              >
                <span className={isActive ? "text-blue-500" : "text-zinc-400"}>
                  {item.icon}
                </span>
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </>
  );
}
