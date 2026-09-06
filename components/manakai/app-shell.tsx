import Link from 'next/link';
import {
  BadgeCheck,
  BookOpenText,
  CircleHelp,
  FlaskConical,
  LayoutDashboard,
  Search,
  Sparkles,
  Stamp,
  Workflow,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const nav = [
  { href: '/', label: 'Overview', icon: LayoutDashboard },
  { href: '/product', label: 'Product analyser', icon: Sparkles },
  {
    href: '/compliance',
    label: 'Compliance journey',
    icon: Workflow,
  },
  { href: '/standards', label: 'Standards', icon: BookOpenText },
  { href: '/labs', label: 'Laboratories', icon: FlaskConical },
  { href: '/ask', label: 'Ask ManakAI', icon: Search },
  { href: '/consumer', label: 'Consumer help', icon: Stamp },
];

export function AppShell({
  children,
  current,
}: {
  children: React.ReactNode;
  current?: string;
}) {
  const isStaging = process.env.NEXT_PUBLIC_APP_ENV === 'staging';
  return (
    <main className="min-h-screen bg-background text-foreground">
      {isStaging && (
        <div className="border-b border-amber-300/20 bg-amber-300/10 px-4 py-2 text-center text-[11px] leading-4 text-amber-100">
          <strong>ManakAI — Prototype / Staging.</strong> Guidance is based on integrated BIS sources and should be independently verified before operational or legal decisions.
        </div>
      )}
      <header className="sticky top-0 z-40 border-b border-border/80 bg-background/90 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-[1500px] items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              aria-label="ManakAI home"
              className="grid size-9 place-items-center rounded-md bg-primary text-primary-foreground"
            >
              <BadgeCheck className="size-5" />
            </Link>
            <div>
              <Link
                href="/"
                className="font-heading text-[17px] font-semibold tracking-[-0.04em]"
              >
                ManakAI
              </Link>
              <div className="hidden text-[10px] uppercase tracking-[0.14em] text-muted-foreground sm:block">
                Standards intelligence
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className="hidden border-cyan-400/20 bg-cyan-400/5 text-cyan-300 sm:inline-flex"
            >
              <span className="size-1.5 rounded-full bg-cyan-300" /> Source-aware
              dataset
            </Badge>
            <Badge variant="outline" className="h-9 rounded-md border-border bg-card px-3 text-muted-foreground">
              EN · हिं · Hinglish
            </Badge>
          </div>
        </div>
      </header>
      <nav aria-label="Mobile primary" className="flex gap-1 overflow-x-auto border-b border-border px-3 py-2 lg:hidden">
        {nav.map(({ href, label }) => (
          <Link key={href} href={href} className={`shrink-0 rounded-md px-3 py-2 text-xs ${current === href ? 'bg-primary/15 text-primary' : 'text-muted-foreground'}`}>
            {label}
          </Link>
        ))}
      </nav>
      <div className="mx-auto grid max-w-[1500px] lg:grid-cols-[220px_minmax(0,1fr)]">
        <aside className="hidden min-h-[calc(100vh-64px)] border-r border-border px-3 py-5 lg:flex lg:flex-col">
          <nav aria-label="Primary" className="space-y-1">
            {nav.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                className={`nav-item ${current === href ? 'nav-active' : ''}`}
                href={href}
              >
                <Icon /> {label}
              </Link>
            ))}
          </nav>
          <div className="mt-auto space-y-2">
            <Link href="/about" className="nav-item">
              <CircleHelp /> About & architecture
            </Link>
            <div className="rounded-lg border border-border bg-card p-3">
              <div className="mb-2 flex items-center gap-2 text-xs font-medium">
                <CircleHelp className="size-4 text-primary" /> Evidence-first by
                design
              </div>
              <p className="text-[11px] leading-4 text-muted-foreground">
                Authoritative, derived, demo and unverified records are labelled. Resolve warnings before relying on a compliance decision.
              </p>
            </div>
          </div>
        </aside>
        <div className="min-w-0">{children}</div>
      </div>
      <footer className="border-t border-border px-4 py-4 text-center text-[11px] leading-5 text-muted-foreground">
        Prototype regulatory navigation only. Confirm current requirements and source validity with BIS or qualified advisers before acting.
      </footer>
    </main>
  );
}

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-7 flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h1 className="mt-2 font-heading text-3xl font-medium tracking-[-0.055em] sm:text-[38px]">
          {title}
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
          {description}
        </p>
      </div>
      {action}
    </div>
  );
}
