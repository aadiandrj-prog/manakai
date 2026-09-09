'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowRight, BookOpenText, FlaskConical, Search, ShieldCheck, Stamp } from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { ActionLink } from '@/components/manakai/action-link';
import { api } from '@/lib/api-client';

const secondaryActions = [
  { href: '/ask', icon: BookOpenText, title: 'Ask about a standard', copy: 'Ask a question and inspect the evidence used in the answer.' },
  { href: '/labs', icon: FlaskConical, title: 'Find a testing lab', copy: 'Search available BIS-recognised scope records by standard and date.' },
  { href: '/consumer', icon: Stamp, title: 'Consumer help', copy: 'Understand certification marks, hallmarking, HUID and complaint routes.' },
];

export default function Home() {
  const [query, setQuery] = useState('');
  const coverageQuery = useQuery({ queryKey: ['coverage'], queryFn: api.coverage });
  const coverageStatsQuery = useQuery({ queryKey: ['coverage-stats'], queryFn: api.coverageStats });
  return (
    <AppShell current="/">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-12">
        <div className="mx-auto max-w-[1120px]">
          <PageHeader eyebrow="BIS compliance guidance" title="Check what applies to your product" description="Describe what you manufacture, import, or sell. ManakAI will show the supported BIS status, applicable standard, important date, evidence, and your next step." />
          <div className="analysis-box border-primary/25 p-5 sm:p-7">
            <div className="flex items-center gap-2 text-sm font-medium"><Search className="size-4 text-primary" /> Check my product</div>
            <label htmlFor="product-query" className="mt-4 block text-sm text-muted-foreground">What product do you make, import, or sell?</label>
            <div className="mt-2 flex flex-col gap-3 sm:flex-row">
              <input id="product-query" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="For example: I manufacture a 1500 W household electric kettle" className="min-h-12 flex-1 rounded-md border border-input bg-[#0b0c0d] px-4 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20" />
              <ActionLink ariaLabel="Check my product" href={query.trim() ? `/product?q=${encodeURIComponent(query)}` : '/product'} className="min-h-12 px-6">Check my product <ArrowRight /></ActionLink>
            </div>
            <p className="mt-3 text-xs leading-5 text-muted-foreground">Include the product type and intended use. Add voltage, wattage, grade, capacity, or fineness when you know it.</p>
          </div>
          <section className="mt-7" aria-labelledby="other-actions">
            <div className="mb-4 flex items-center justify-between gap-4"><h2 id="other-actions" className="font-heading text-lg tracking-[-0.03em]">Other ways to use ManakAI</h2><span className="text-xs text-muted-foreground">Choose one clear task</span></div>
            <div className="grid gap-3 md:grid-cols-3">{secondaryActions.map(({ href, icon: Icon, title, copy }) => <Link key={title} href={href} className="workflow-card group min-h-44"><div className="icon-box cyan"><Icon /></div><div className="mt-6 flex items-center justify-between gap-3"><h3 className="font-heading text-base font-medium tracking-[-0.03em]">{title}</h3><ArrowRight className="size-4 shrink-0 text-muted-foreground transition group-hover:translate-x-1 group-hover:text-foreground" /></div><p className="mt-2 text-xs leading-5 text-muted-foreground">{copy}</p></Link>)}</div>
          </section>
          <section className="mt-7 panel p-5" aria-labelledby="coverage-heading">
            <div className="flex flex-wrap items-end justify-between gap-3"><div><span className="eyebrow">Available today</span><h2 id="coverage-heading" className="mt-2 font-heading text-lg tracking-[-.03em]">Products ManakAI currently covers</h2></div><span className="text-xs text-muted-foreground">{coverageStatsQuery.data ? `${coverageStatsQuery.data.verified} verified · ${coverageStatsQuery.data.partial} partial` : 'Loading coverage…'}</span></div>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">{(coverageQuery.data ?? []).slice(0, 6).map((item) => <article key={item.id} className="rounded-md border border-border bg-[#0c0d0e] p-3"><div className="flex items-start justify-between gap-2"><p className="text-sm font-medium">{item.category_name}</p><span className={`rounded px-1.5 py-0.5 text-[9px] ${item.coverage_status === 'VERIFIED' ? 'bg-emerald-400/10 text-emerald-300' : 'bg-amber-300/10 text-amber-300'}`}>{item.coverage_status === 'VERIFIED' ? 'Verified coverage' : 'Partial coverage'}</span></div><p className="mt-2 text-xs text-muted-foreground">{item.primary_standard ?? 'Standard not fully verified'}</p></article>)}</div>
            <Link href="/coverage" className="mt-4 inline-flex items-center gap-2 text-xs font-medium text-primary">Browse all published coverage <ArrowRight className="size-3" /></Link>
            <div className="mt-4 flex gap-3 rounded-md border border-cyan-300/20 bg-cyan-300/5 p-3"><ShieldCheck className="mt-0.5 size-4 shrink-0 text-cyan-300" /><p className="text-xs leading-5 text-cyan-50/70">If a product is not covered, ManakAI will say so. It will not guess a compliance conclusion from general AI knowledge.</p></div>
          </section>
        </div>
      </section>
    </AppShell>
  );
}
