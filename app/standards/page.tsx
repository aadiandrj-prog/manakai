'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowUpRight, BookOpenText, Search } from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { Badge } from '@/components/ui/badge';
import { ErrorState, LoadingState } from '@/components/manakai/data-state';
import { api, errorMessage } from '@/lib/api-client';

export default function StandardsPage() {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('All');
  const standardsQuery = useQuery({ queryKey: ['standards'], queryFn: () => api.standards() });
  const standards = standardsQuery.data ?? [];
  const categories = [
    'All',
    ...Array.from(new Set(standards.map((item) => item.category))),
  ];
  const filtered = standards.filter(
    (item) =>
      (category === 'All' || item.category === category) &&
      `${item.number} ${item.title}`.toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <AppShell current="/standards">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1180px]">
          <PageHeader
            eyebrow="Ask about a standard"
            title="Find an Indian Standard"
            description="Search the standard number, product, or title. Open a result to see its scope, related standards, source status, and available testing information."
            action={
              <Badge
                variant="outline"
                className="border-cyan-300/20 text-cyan-300"
              >
                {standards.length} available records
              </Badge>
            }
          />
          <div className="panel mb-5 flex flex-col gap-3 p-4 md:flex-row">
            <label className="relative flex-1" aria-label="Search standards">
              <Search className="absolute left-3 top-3 size-4 text-muted-foreground" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="h-10 w-full rounded-md border border-input bg-[#0b0c0d] pl-9 pr-3 text-sm outline-none focus:border-primary"
                placeholder="Search standard number, title or product…"
              />
            </label>
            <select aria-label="Filter by product category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="h-10 rounded-md border border-input bg-[#0b0c0d] px-3 text-sm"
            >
              {categories.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
          </div>
          <div className="panel overflow-hidden">
            {standardsQuery.isPending && <LoadingState label="Loading standards from the database…" />}
            {standardsQuery.isError && <ErrorState message={errorMessage(standardsQuery.error)} onRetry={() => { void standardsQuery.refetch(); }} />}
            {standardsQuery.isSuccess && <>
            <div className="hidden grid-cols-[1.1fr_2fr_.7fr_.7fr_36px] border-b border-border px-5 py-3 text-[10px] uppercase tracking-[.1em] text-muted-foreground md:grid">
              <span>Standard</span>
              <span>Title</span>
              <span>Category</span>
              <span>Status</span>
              <span />
            </div>
            {filtered.map((item) => (
              <Link
                href={`/standards/${item.id}`}
                key={item.id}
                className="grid gap-2 border-b border-border px-5 py-4 transition last:border-0 hover:bg-muted/50 md:grid-cols-[1.1fr_2fr_.7fr_.7fr_36px] md:items-center"
              >
                <div>
                  <span className="font-heading text-sm font-medium">
                    {item.number}
                  </span>
                  <span className="ml-2 text-[10px] text-muted-foreground">
                    :{item.version}
                  </span>
                </div>
                <div className="text-xs leading-5 text-muted-foreground">
                  {item.title}
                </div>
                <div className="text-xs text-muted-foreground">
                  {item.category}
                </div>
                <Badge
                  variant="outline"
                  className={
                    item.status === 'ACTIVE'
                      ? 'border-emerald-300/20 text-emerald-300'
                      : 'border-amber-300/20 text-amber-300'
                  }
                >
                  {item.status}
                </Badge>
                <ArrowUpRight className="size-4 text-muted-foreground" />
              </Link>
            ))}
            {filtered.length === 0 && (
              <div className="grid min-h-56 place-items-center text-center">
                <div>
                  <BookOpenText className="mx-auto size-6 text-muted-foreground" />
                  <p className="mt-3 text-sm">
                    No available standards match this search.
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Try a standard number or a broader category.
                  </p>
                </div>
              </div>
            )}
            </>}
          </div>
        </div>
      </section>
    </AppShell>
  );
}
