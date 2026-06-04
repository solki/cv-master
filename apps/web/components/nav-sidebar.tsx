"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useStore } from "@/lib/store";
import { NavIcons } from "@/components/icons";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard" },
  { href: "/profile", label: "Career Profile" },
  { href: "/projects", label: "Projects" },
  { href: "/evidence", label: "Evidence" },
  { href: "/jd", label: "JD Analyzer" },
  { href: "/resumes", label: "Resume Generator" },
  { href: "/library", label: "Resume Library" },
  { href: "/vault", label: "Vault" },
  { href: "/settings", label: "Settings" },
];

export default function NavSidebar() {
  const pathname = usePathname();
  const sidebarOpen = useStore((s) => s.sidebarOpen);
  const toggleSidebar = useStore((s) => s.toggleSidebar);
  const setSidebarOpen = useStore((s) => s.setSidebarOpen);

  return (
    <>
      {/* Skip to content */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-[100] focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded focus:shadow-lg"
      >
        Skip to content
      </a>

      {/* Mobile hamburger button */}
      <button
        onClick={toggleSidebar}
        className="md:hidden fixed top-3 left-3 z-50 p-2 rounded-md bg-slate-900 border border-slate-700 shadow-sm hover:bg-slate-800 transition-colors"
        aria-label={sidebarOpen ? "Close navigation" : "Open navigation"}
        aria-expanded={sidebarOpen}
      >
        <svg className="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
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
          className="md:hidden fixed inset-0 bg-black/60 z-30"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <nav
        className={`w-56 bg-slate-900 border-r border-slate-700 flex-shrink-0 flex-col z-40
          fixed inset-y-0 left-0 transition-transform duration-200 md:relative md:flex
          ${sidebarOpen ? "translate-x-0 flex" : "-translate-x-full md:translate-x-0 md:flex"}`}
        aria-label="Main navigation"
      >
        <div className="p-4 font-bold text-lg border-b border-slate-800 text-slate-100">
          CV Master
        </div>
        <div className="flex-1 py-2 overflow-y-auto" role="list">
          {NAV_ITEMS.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            const Icon = NavIcons[item.href];
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                  isActive
                    ? "bg-blue-950 text-blue-300 font-medium border-l-2 border-blue-500"
                    : "text-slate-300 hover:bg-slate-800 hover:text-slate-100 border-l-2 border-transparent"
                }`}
                aria-current={isActive ? "page" : undefined}
                role="listitem"
              >
                {Icon && (
                  <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? "text-blue-400" : "text-slate-500"}`} />
                )}
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </>
  );
}
