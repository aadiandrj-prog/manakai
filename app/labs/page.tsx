'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FlaskConical, MapPin, Search, ShieldAlert } from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { Badge } from '@/components/ui/badge';
import { ErrorState, LoadingState } from '@/components/manakai/data-state';
import { api, errorMessage } from '@/lib/api-client';

export default function LabsPage() {
  const [query, setQuery] = useState('');
  const [standard, setStandard] = useState('All standards');
  const [asOfDate, setAsOfDate] = useState(new Date().toISOString().slice(0, 10));
  const standardsQuery = useQuery({ queryKey: ['standards'], queryFn: () => api.standards() });
  const labsQuery = useQuery({
    queryKey: ['labs', query, standard, asOfDate],
    queryFn: () => api.searchLabs({ query, standard_number: standard === 'All standards' ? null : standard, location: null, as_of_date: asOfDate }),
  });
  const filtered = labsQuery.data ?? [];
  return (
    <AppShell current="/labs">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1180px]">
          <PageHeader
            eyebrow="Act"
            title="Testing laboratory finder"
            description="Match a standard and testing need against source-labelled recognition records, filtered to the selected date where validity is known."
            action={
              <Badge
                variant="outline"
                className="border-amber-300/20 text-amber-300"
              >
                Source-aware records
              </Badge>
            }
          />
          <div className="mb-5 flex gap-3 rounded-md border border-amber-300/20 bg-amber-300/5 p-4">
            <ShieldAlert className="mt-0.5 size-4 shrink-0 text-amber-300" />
            <p className="text-xs leading-5 text-amber-100/70">
              Confirm the precise scope, exclusions and validity in the linked BIS LIMS record before booking testing. Records without confirmable validity are not recommended as current.
            </p>
          </div>
          <div className="panel mb-5 grid gap-3 p-4 md:grid-cols-3">
            <label className="relative">
              <Search className="absolute left-3 top-3 size-4 text-muted-foreground" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="City, state, test or laboratory…"
                className="h-10 w-full rounded-md border border-input bg-[#0b0c0d] pl-9 pr-3 text-sm outline-none focus:border-primary"
              />
            </label>
            <select
              value={standard}
              onChange={(e) => setStandard(e.target.value)}
              className="h-10 rounded-md border border-input bg-[#0b0c0d] px-3 text-sm"
            >
              <option>All standards</option>
              {(standardsQuery.data ?? []).map((item) => (
                <option key={item.id}>{item.number}</option>
              ))}
            </select>
            <input aria-label="Recognition valid as of" type="date" value={asOfDate} onChange={(event) => setAsOfDate(event.target.value)} className="h-10 rounded-md border border-input bg-[#0b0c0d] px-3 text-sm" />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {labsQuery.isPending && <div className="col-span-full"><LoadingState label="Searching laboratory records…" /></div>}
            {labsQuery.isError && <div className="col-span-full"><ErrorState message={errorMessage(labsQuery.error)} /></div>}
            {filtered.map((lab) => (
              <article key={lab.id} className="panel p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="grid size-9 place-items-center rounded-md border border-cyan-300/20 bg-cyan-300/5">
                    <FlaskConical className="size-4 text-cyan-300" />
                  </div>
                  <Badge
                    variant="outline"
                    className="border-amber-300/20 text-amber-300"
                  >
                    {lab.source_kind === 'AUTHORITATIVE' ? 'Verified BIS source' : lab.source_kind === 'DEMO' ? 'Demo data' : lab.source_kind}
                  </Badge>
                </div>
                <h2 className="mt-5 font-heading text-lg tracking-[-.035em]">
                  {lab.name}
                </h2>
                <p className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                  <MapPin className="size-3" />
                  {lab.city}, {lab.state}
                </p>
                <div className="mt-4">
                  <div className="eyebrow">Mapped standards</div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {lab.standards.map((item) => (
                      <Badge key={item} variant="outline">
                        {item}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="mt-4 text-xs text-muted-foreground">
                  <div>Recognition: {lab.recognition_status} · valid until {lab.valid_until ?? 'not confirmed'}</div>
                  {lab.scope_identifier && <div className="mt-1">{lab.scope_identifier}</div>}
                  {lab.source_url && <a className="mt-2 inline-block text-primary hover:underline" href={lab.source_url} target="_blank" rel="noreferrer">View BIS LIMS source</a>}
                  {lab.warning && <p className="mt-2 text-amber-300">{lab.warning}</p>}
                </div>
                <div className="mt-4">
                  <div className="eyebrow">Capabilities</div>
                  <p className="mt-2 text-xs leading-5 text-muted-foreground">
                    {lab.capabilities.join(' · ')}
                  </p>
                </div>
              </article>
            ))}
            {labsQuery.isSuccess && filtered.length === 0 && (
              <div className="panel col-span-full grid min-h-56 place-items-center text-center">
                <div>
                  <FlaskConical className="mx-auto size-6 text-muted-foreground" />
                  <p className="mt-3 text-sm">No recognised laboratory matched this date and scope.</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Clear a filter or try another test capability.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </AppShell>
  );
}
