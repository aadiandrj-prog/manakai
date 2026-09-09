'use client';

import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowRight, Search, ShieldCheck } from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { ErrorState, LoadingState } from '@/components/manakai/data-state';
import { api, errorMessage } from '@/lib/api-client';

export default function CoveragePage() {
  const [query, setQuery] = useState('');
  const coverage = useQuery({ queryKey: ['coverage'], queryFn: api.coverage });
  const stats = useQuery({ queryKey: ['coverage-stats'], queryFn: api.coverageStats });
  const items = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return coverage.data ?? [];
    return (coverage.data ?? []).filter((item) => [item.category_name, item.category_slug, item.primary_standard, item.product_group, ...(item.aliases ?? [])].filter(Boolean).join(' ').toLowerCase().includes(needle));
  }, [coverage.data, query]);

  return <AppShell current="/coverage"><section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10"><div className="mx-auto max-w-[1120px]">
    <PageHeader eyebrow="Published coverage" title="What ManakAI can verify today" description="Browse the product families that have passed the coverage review workflow. Partial coverage is useful metadata, but it is not presented as a complete compliance conclusion." />
    <div className="grid gap-3 sm:grid-cols-3">
      <Metric label="Published families" value={stats.data?.total ?? '—'} />
      <Metric label="Verified end-to-end" value={stats.data?.verified ?? '—'} />
      <Metric label="Explicitly partial" value={stats.data?.partial ?? '—'} />
    </div>
    <label className="mt-5 flex min-h-12 items-center gap-3 rounded-md border border-input bg-[#0b0c0d] px-4"><Search className="size-4 text-primary" /><span className="sr-only">Search coverage</span><input value={query} onChange={(event) => setQuery(event.target.value)} className="h-11 flex-1 bg-transparent text-sm outline-none" placeholder="Search by product, alias, group, or standard" /></label>
    {coverage.isPending && <div className="mt-5"><LoadingState label="Loading published coverage…" /></div>}
    {coverage.isError && <div className="mt-5"><ErrorState message={errorMessage(coverage.error)} onRetry={() => coverage.refetch()} /></div>}
    <div className="mt-5 grid gap-4 md:grid-cols-2">{items.map((item) => <article key={item.id} className="panel p-5">
      <div className="flex items-start justify-between gap-3"><div><p className="text-[10px] uppercase tracking-[.12em] text-muted-foreground">{item.product_group ?? 'Product family'}</p><h2 className="mt-2 font-heading text-lg">{item.category_name}</h2></div><span className={`rounded px-2 py-1 text-[10px] ${item.coverage_status === 'VERIFIED' ? 'bg-emerald-400/10 text-emerald-300' : 'bg-amber-300/10 text-amber-300'}`}>{item.coverage_status}</span></div>
      <p className="mt-3 text-sm text-primary">{item.primary_standard ?? 'Standard metadata incomplete'}</p><p className="mt-3 text-xs leading-5 text-muted-foreground">{item.coverage_reason}</p>
      <div className="mt-4 flex flex-wrap gap-2 text-[10px] text-muted-foreground"><span className="rounded border border-border px-2 py-1">{item.authoritative_sources_count} source records</span><span className="rounded border border-border px-2 py-1">Labs: {item.lab_completeness.replaceAll('_', ' ').toLowerCase()}</span></div>
      {item.known_limitations.length > 0 && <details className="mt-4 border-t border-border pt-3"><summary className="cursor-pointer text-xs text-amber-300">What still needs confirmation</summary><ul className="mt-2 space-y-1 text-xs leading-5 text-muted-foreground">{item.known_limitations.map((value) => <li key={value}>• {value}</li>)}</ul></details>}
      <Link href={`/product?q=${encodeURIComponent(`I manufacture ${item.category_name} in India`)}`} className="mt-4 inline-flex items-center gap-2 text-xs font-medium text-primary">Check this product <ArrowRight className="size-3" /></Link>
    </article>)}</div>
    {!coverage.isPending && items.length === 0 && <div className="panel mt-5 p-7 text-center"><ShieldCheck className="mx-auto size-5 text-primary" /><p className="mt-3 text-sm">No published family matches that search.</p><p className="mt-2 text-xs text-muted-foreground">You can still describe the product freely; ManakAI will return an unsupported or clarification result rather than guess.</p></div>}
  </div></section></AppShell>;
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}
