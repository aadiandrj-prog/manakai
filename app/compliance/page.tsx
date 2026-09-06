'use client';

import { useMemo, useSyncExternalStore } from 'react';
import { ArrowRight, CheckCircle2, ClipboardList, Search, ShieldCheck } from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { ActionLink } from '@/components/manakai/action-link';

type RecentProfile = { id: string; product: string; status: string; asOfDate: string };

export default function ComplianceLandingPage() {
  const saved = useSyncExternalStore(subscribeRecent, readRecent, () => null);
  const recent = useMemo(() => {
    try { return saved ? JSON.parse(saved) as RecentProfile : null; } catch { return null; }
  }, [saved]);

  return (
    <AppShell current="/compliance">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1040px]">
          <PageHeader eyebrow="Your action plan" title="Compliance journey" description="Start with a product analysis. ManakAI will then turn the supported regulatory result into a clear, evidence-linked action plan." />
          {recent ? (
            <div className="panel overflow-hidden">
              <div className="panel-header">
                <div><span className="eyebrow">Most recent result on this device</span><h2 className="panel-title">{recent.product}</h2><p className="mt-1 text-xs text-muted-foreground">Status on {formatDate(recent.asOfDate)}: {recent.status}</p></div>
                <ShieldCheck className="size-5 text-emerald-300" />
              </div>
              <div className="p-5"><p className="max-w-2xl text-sm leading-6 text-muted-foreground">Continue to the result, review any missing information, and follow the first incomplete step. This shortcut is stored only in this browser.</p><ActionLink href={`/compliance/${recent.id}`} className="mt-5">Continue this journey <ArrowRight /></ActionLink></div>
            </div>
          ) : (
            <div className="panel grid min-h-72 place-items-center px-5 text-center">
              <div className="max-w-lg"><ClipboardList className="mx-auto size-8 text-primary" /><h2 className="mt-4 font-heading text-xl">No compliance journey yet</h2><p className="mt-2 text-sm leading-6 text-muted-foreground">Describe what you manufacture, import, or sell. Once ManakAI identifies supported coverage, your result and next actions will appear here.</p><ActionLink href="/product" className="mt-5"><Search /> Check my product</ActionLink></div>
            </div>
          )}
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            {[
              ['1', 'Describe the product', 'Include its purpose, type, rating, grade, or capacity when known.'],
              ['2', 'Review the result', 'Confirm the identified product, status, effective date, and missing details.'],
              ['3', 'Follow the actions', 'Inspect the standard, evidence, testing route, and recognised services.'],
            ].map(([number, title, copy]) => <article key={number} className="panel p-4"><div className="flex items-center gap-2 text-sm font-medium"><span className="grid size-6 place-items-center rounded-full border border-primary/30 text-[10px] text-primary">{number}</span>{title}</div><p className="mt-3 text-xs leading-5 text-muted-foreground">{copy}</p></article>)}
          </div>
          <div className="mt-5 flex gap-3 rounded-md border border-emerald-300/20 bg-emerald-300/5 p-4 text-xs leading-5 text-emerald-50/70"><CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-300" />A journey is generated only from the saved compliance profile. The sidebar no longer opens a synthetic demo record.</div>
        </div>
      </section>
    </AppShell>
  );
}

function subscribeRecent() { return () => undefined; }
function readRecent() { return window.localStorage.getItem('manakai:last-compliance-profile'); }

function formatDate(value: string) {
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' });
}
