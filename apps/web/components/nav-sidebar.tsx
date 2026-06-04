"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

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

  return (
    <nav className="w-56 bg-white border-r border-zinc-200 flex-shrink-0 hidden md:flex flex-col">
      <div className="p-4 font-bold text-lg border-b border-zinc-100">
        CV Master
      </div>
      <div className="flex-1 py-2">
        {NAV_ITEMS.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
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
  );
}
