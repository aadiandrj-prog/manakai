'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  BookOpenText,
  CheckCircle2,
  FlaskConical,
  Search,
  ShieldCheck,
  Sparkles,
  Stamp,
  Workflow,
} from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { Button } from '@/components/ui/button';

const workflows = [
  {
    href: '/product',
    icon: Search,
    title: 'Find standards',
    copy: 'Describe a product and identify likely Indian Standards.',
    accent: 'violet',
  },
  {
    href: '/product',
    icon: ShieldCheck,
    title: 'Check certification',
    copy: 'Understand mandatory status, QCOs and schemes.',
    accent: 'cyan',
  },
  {
    href: '/compliance/demo-emergency-lamp',
    icon: Workflow,
    title: 'Build compliance journey',
    copy: 'Turn requirements into a trackable action plan.',
    accent: 'orange',
  },
  {
    href: '/labs',
    icon: FlaskConical,
    title: 'Find testing labs',
    copy: 'Search seeded laboratory capability records.',
    accent: 'green',
  },
  {
    href: '/ask',
    icon: BookOpenText,
    title: 'Ask a technical question',
    copy: 'Get evidence-first answers with clause citations.',
    accent: 'violet',
  },
  {
    href: '/consumer',
    icon: Stamp,
    title: 'Consumer & hallmarking',
    copy: 'Understand marks, HUID and complaint routes.',
    accent: 'cyan',
  },
];

export default function Home() {
  const [query, setQuery] = useState('');
  return (
    <AppShell current="/">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1180px]">
          <PageHeader
            eyebrow="Compliance workspace"
            title="What are you trying to do?"
            description="Move from product description to standards, certification status, testing evidence and next actions—without losing the regulatory trail."
            action={
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span className="size-2 rounded-full bg-emerald-400 shadow-[0_0_12px_#34d399]" />{' '}
                Demo engine ready
              </div>
            }
          />
          <div className="analysis-box mb-7">
            <div className="flex items-center gap-2 text-xs font-medium text-primary">
              <Sparkles className="size-4" /> INTENT ROUTER
            </div>
            <label
              htmlFor="product-query"
              className="mt-4 block font-heading text-xl tracking-[-0.035em]"
            >
              Describe your product or ask anything about BIS
            </label>
            <div className="mt-4 flex flex-col gap-2 sm:flex-row">
              <input
                id="product-query"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="e.g. I manufacture a portable rechargeable LED emergency lamp"
                className="h-12 flex-1 rounded-md border border-input bg-[#0b0c0d] px-4 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
              <Button
                nativeButton={false}
                render={
                  <Link
                    aria-label="Route request to the product analyser"
                    href={
                      query.trim()
                        ? `/product?q=${encodeURIComponent(query)}`
                        : '/product'
                    }
                  />
                }
                className="h-12 rounded-md bg-primary px-5 text-primary-foreground"
              >
                Route request <ArrowRight />
              </Button>
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-muted-foreground">
              <span>Try:</span>
              {[
                'electric kettle certification',
                'clause 6.3 explained',
                'labs near Delhi',
                'verify jewellery HUID',
              ].map((item) => (
                <button
                  key={item}
                  onClick={() => setQuery(item)}
                  className="rounded border border-border px-2 py-1 hover:bg-muted"
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-heading text-lg tracking-[-0.03em]">
              Choose a workflow
            </h2>
            <span className="text-xs text-muted-foreground">
              6 specialised paths
            </span>
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {workflows.map(({ href, icon: Icon, title, copy, accent }) => (
              <Link
                key={title}
                href={href}
                className="workflow-card group text-left"
              >
                <div className={`icon-box ${accent}`}>
                  <Icon />
                </div>
                <div className="mt-7 flex items-center justify-between">
                  <h3 className="font-heading text-base font-medium tracking-[-0.03em]">
                    {title}
                  </h3>
                  <ArrowRight className="size-4 text-muted-foreground transition group-hover:translate-x-1 group-hover:text-foreground" />
                </div>
                <p className="mt-2 text-xs leading-5 text-muted-foreground">
                  {copy}
                </p>
              </Link>
            ))}
          </div>
          <section className="mt-7 grid gap-4 lg:grid-cols-[1.1fr_.9fr]">
            <div className="panel p-5">
              <span className="eyebrow">Operational overview</span>
              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                <div>
                  <div className="font-heading text-3xl tracking-[-.05em]">
                    5
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    seeded standard records
                  </p>
                </div>
                <div>
                  <div className="font-heading text-3xl tracking-[-.05em]">
                    4
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    demo lab records
                  </p>
                </div>
                <div>
                  <div className="font-heading text-3xl tracking-[-.05em]">
                    3
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    reliable demo paths
                  </p>
                </div>
              </div>
            </div>
            <div className="panel p-5">
              <span className="eyebrow">System discipline</span>
              <div className="mt-4 flex gap-3">
                <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-300" />
                <div>
                  <p className="text-sm font-medium">
                    No unsupported legal claims
                  </p>
                  <p className="mt-1 text-xs leading-5 text-muted-foreground">
                    Unverified requirements are surfaced as uncertainty, with
                    the missing evidence made explicit.
                  </p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </section>
    </AppShell>
  );
}
