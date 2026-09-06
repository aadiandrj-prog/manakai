'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  CheckCircle2,
  ExternalLink,
  ScanLine,
  ShieldCheck,
  Stamp,
  TriangleAlert,
} from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { ErrorState, LoadingState } from '@/components/manakai/data-state';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api-client';

const help = [
  {
    icon: ScanLine,
    title: 'Understand HUID',
    copy: 'Learn what the Hallmark Unique Identification code represents and what details to compare.',
    href: '#verify-huid',
  },
  {
    icon: ShieldCheck,
    title: 'Check a certification mark',
    copy: 'Identify the mark and use the appropriate official verification route.',
    href: '#identify-hallmark',
  },
  {
    icon: TriangleAlert,
    title: 'Report a concern',
    copy: 'Collect invoice, product, mark and seller details before filing through an official channel.',
    href: '#consumer-testing',
  },
];

export default function ConsumerPage() {
  const [huid, setHuid] = useState('');
  const [checked, setChecked] = useState(false);
  const guidance = useQuery({ queryKey: ['hallmarking-guidance'], queryFn: api.hallmarkingGuidance });
  const officialServiceUrl = guidance.data?.find((item) => item.topic === 'verify-huid')?.source_url;
  return (
    <AppShell current="/consumer">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1100px]">
          <PageHeader
            eyebrow="Consumer mode"
            title="Marks, hallmarking and product help"
            description="A separate, plain-language path for consumers. ManakAI explains what to check and routes you to official services without pretending to perform a live verification."
          />
          <div className="grid gap-4 md:grid-cols-3">
            {help.map(({ icon: Icon, title, copy, href }) => (
              <a key={title} href={href} className="workflow-card group min-h-44">
                <div className="icon-box cyan">
                  <Icon />
                </div>
                <h2 className="mt-7 font-heading text-base tracking-[-.03em]">
                  {title}
                </h2>
                <p className="mt-2 text-xs leading-5 text-muted-foreground">
                  {copy}
                </p>
                <span className="mt-4 inline-block text-xs text-primary">View guidance ↓</span>
              </a>
            ))}
          </div>
          <div className="mt-5 grid gap-5 lg:grid-cols-[.85fr_1.15fr]">
            <div className="panel p-5">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Stamp className="size-4 text-primary" /> HUID verification boundary
              </div>
              <label
                htmlFor="huid"
                className="mt-5 block text-xs text-muted-foreground"
              >
                Enter the 6-character HUID printed on the jewellery
              </label>
              <input
                id="huid"
                value={huid}
                maxLength={6}
                onChange={(e) => {
                  setHuid(e.target.value.toUpperCase());
                  setChecked(false);
                }}
                placeholder="ABC123"
                className="mt-2 h-11 w-full rounded-md border border-input bg-[#0b0c0d] px-3 font-mono uppercase tracking-[.25em] outline-none focus:border-primary"
              />
              <Button
                onClick={() => setChecked(true)}
                disabled={huid.length !== 6}
                className="mt-3 w-full rounded-md"
              >
                Explain how to verify
              </Button>
              {checked && (
                <div className="mt-4 rounded-md border border-cyan-300/20 bg-cyan-300/5 p-3 text-xs leading-5 text-cyan-50/70">
                  <CheckCircle2 className="mb-2 size-4 text-cyan-300" />
                  Format captured. ManakAI does not query or verify the HUID.
                  Use Verify HUID in the official BIS Care app and compare the displayed
                  article type, jeweller and hallmarking centre with your item
                  and invoice.
                </div>
              )}
            </div>
            <div className="panel p-5">
              <span className="eyebrow">Safe verification sequence</span>
              <ol className="mt-5 space-y-4">
                {[
                  'Locate the BIS hallmark and six-character alphanumeric HUID on the item.',
                  'Use the current official BIS consumer verification service.',
                  'Compare jeweller, article type, purity and hallmarking-centre details.',
                  'Keep the invoice. If details conflict, contact the seller and use the official complaint route.',
                ].map((item, index) => (
                  <li key={item} className="flex gap-3">
                    <span className="grid size-6 shrink-0 place-items-center rounded-full border border-primary/30 bg-primary/5 text-[10px] text-primary">
                      {index + 1}
                    </span>
                    <p className="text-xs leading-5 text-muted-foreground">
                      {item}
                    </p>
                  </li>
                ))}
              </ol>
              {officialServiceUrl && <a aria-label="Open official BIS Care guidance" href={officialServiceUrl} target="_blank" rel="noreferrer" className="mt-5 inline-flex h-9 items-center gap-2 rounded-md border border-input px-4 text-sm font-medium hover:bg-muted">Open official BIS Care guidance <ExternalLink className="size-4" /></a>}
              <p className="mt-2 text-[10px] text-muted-foreground">
                HUID verification is available in the official BIS Care mobile app, not through a public ManakAI integration.
              </p>
            </div>
          </div>
          {guidance.isPending && <div className="mt-5"><LoadingState label="Loading official consumer guidance…" /></div>}
          {guidance.isError && <div className="mt-5"><ErrorState message="We couldn’t load the official consumer-guidance links. Try again shortly; do not rely on an unverified HUID result." onRetry={() => { void guidance.refetch(); }} /></div>}
          {guidance.data && <section className="mt-5 panel p-5"><span className="eyebrow">Official consumer guidance</span><div className="mt-4 grid gap-3 md:grid-cols-3">{guidance.data.map((item) => <article id={item.topic} key={item.id} className="scroll-mt-24 rounded-md border border-border bg-[#0c0d0e] p-4"><h2 className="text-sm font-medium">{item.title}</h2><ol className="mt-3 space-y-2 text-xs leading-5 text-muted-foreground">{item.guidance.map((step, index) => <li key={step}>{index + 1}. {step}</li>)}</ol><a className="mt-3 inline-flex min-h-10 items-center gap-1 text-xs text-primary hover:underline" href={item.source_url} target="_blank" rel="noreferrer">Open official BIS guidance <ExternalLink className="size-3" /></a></article>)}</div></section>}
        </div>
      </section>
    </AppShell>
  );
}
