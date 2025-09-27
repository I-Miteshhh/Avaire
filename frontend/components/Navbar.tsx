"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/style-dna", label: "Style DNA" },
  { href: "/catalog", label: "Catalog" },
  { href: "/try-on", label: "Try-On Studio" },
  { href: "/profile", label: "Profile" }
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="fixed inset-x-0 top-0 z-50 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-xl font-semibold tracking-tight">
          Avaire
        </Link>
        <nav className="hidden items-center gap-6 md:flex">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link key={item.href} href={item.href} className="relative text-sm font-medium text-slate-200">
                {item.label}
                {isActive && (
                  <motion.span
                    layoutId="nav-underline"
                    className="absolute inset-x-0 -bottom-1 h-0.5 bg-brand"
                  />
                )}
              </Link>
            );
          })}
        </nav>
        <Link
          href="/style-dna"
          className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-white shadow-glow"
        >
          Find my vibe
        </Link>
      </div>
    </header>
  );
}
