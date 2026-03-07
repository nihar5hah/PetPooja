"use client";

import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard,
  UtensilsCrossed,
  ShoppingCart,
  Sparkles,
  Settings2,
  Mic2,
  Menu,
  X,
  Flame,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/menu", label: "Menu Intel", icon: UtensilsCrossed },
  { href: "/orders", label: "Orders", icon: ShoppingCart },
  { href: "/menu?tab=combos", label: "Combos", icon: Sparkles },
  { href: "/operations", label: "Operations", icon: Settings2 },
  { href: "/voice-lab", label: "Voice Lab", icon: Mic2 },
] as const;

export function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setOpen(true)}
        className="fixed top-4 left-4 z-50 flex size-9 items-center justify-center rounded-lg border border-border bg-card text-foreground lg:hidden"
        aria-label="Open navigation"
      >
        <Menu className="size-4" />
      </button>

      {/* Mobile overlay */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setOpen(false)}
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-56 flex-col border-r border-sidebar-border bg-sidebar transition-transform duration-300 lg:static lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        {/* Brand */}
        <div className="flex h-14 items-center gap-2.5 border-b border-sidebar-border px-5">
          <div className="flex size-7 items-center justify-center rounded-lg bg-primary/15 text-primary">
            <Flame className="size-4" />
          </div>
          <span className="text-sm font-bold tracking-tight text-foreground">
            PetPooja
          </span>
          <button
            onClick={() => setOpen(false)}
            className="ml-auto flex size-7 items-center justify-center rounded-md text-muted-foreground hover:text-foreground lg:hidden"
          >
            <X className="size-4" />
          </button>
        </div>

        {/* Nav items */}
        <nav className="flex-1 space-y-0.5 px-3 py-3">
          {navItems.map(({ href, label, icon: Icon }) => {
            const active = href.startsWith("/menu?") ? pathname === "/menu" : pathname === href;
            return (
              <Link
                key={href}
                href={href as never}
                onClick={() => setOpen(false)}
                className={cn(
                  "group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "text-foreground"
                    : "text-sidebar-foreground hover:text-foreground hover:bg-sidebar-accent",
                )}
              >
                {active && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute inset-0 rounded-lg bg-sidebar-accent border border-border/50"
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}
                <Icon className={cn("relative size-4", active && "text-primary")} />
                <span className="relative">{label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-sidebar-border px-5 py-3">
          <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground/50">
            Revenue Intelligence
          </p>
        </div>
      </aside>
    </>
  );
}
