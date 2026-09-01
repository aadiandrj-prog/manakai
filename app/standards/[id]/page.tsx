import Link from 'next/link';
import { notFound } from 'next/navigation';
import {
  ArrowRight,
  BookOpenText,
  CalendarDays,
  FileText,
  GitBranch,
  ShieldQuestion,
} from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { laboratories, standards } from '@/lib/demo-data';

export default async function StandardDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const standard = standards.find((item) => item.id === id);
  if (!standard) notFound();
  const labs = laboratories.filter((lab) =>
    lab.standards.includes(standard.number),
  );
  return (
    <AppShell current="/standards">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1180px]">
          <PageHeader
            eyebrow={`${standard.category} · Indian Standard`}
            title={`${standard.number}:${standard.version}`}
            description={standard.title}
            action={
              <Badge
                variant="outline"
                className={
                  standard.status === 'ACTIVE'
                    ? 'border-emerald-300/20 text-emerald-300'
                    : 'border-amber-300/20 text-amber-300'
                }
              >
                {standard.status}
              </Badge>
            }
          />
          <div className="grid gap-5 xl:grid-cols-[1.1fr_.9fr]">
            <div className="space-y-5">
              <div className="panel p-5">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <BookOpenText className="size-4 text-primary" /> Scope
                  interpretation
                </div>
                <p className="mt-4 text-sm leading-7 text-muted-foreground">
                  {standard.scope}
                </p>
                <div className="mt-5 flex gap-3 rounded-md border border-cyan-300/20 bg-cyan-300/5 p-3">
                  <FileText className="mt-0.5 size-4 shrink-0 text-cyan-300" />
                  <p className="text-xs leading-5 text-cyan-50/70">
                    This page holds structured demo metadata only. It does not
                    reproduce protected standard text and does not claim live
                    catalogue status.
                  </p>
                </div>
              </div>
              <div className="panel p-5">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <GitBranch className="size-4 text-primary" /> Regulatory
                  relationships
                </div>
                <div className="mt-5 grid gap-3 sm:grid-cols-3">
                  <Relation
                    label="IMPLEMENTED_BY"
                    value="Product manual placeholder"
                  />
                  <Relation
                    label="REGULATED_BY"
                    value="QCO source not connected"
                  />
                  <Relation
                    label="TESTED_USING"
                    value={`${labs.length} matching lab fixtures`}
                  />
                </div>
              </div>
              <div className="panel p-5">
                <span className="eyebrow">Ask about this standard</span>
                <div className="mt-3 flex flex-col gap-2 sm:flex-row">
                  <input
                    className="h-10 flex-1 rounded-md border border-input bg-[#0b0c0d] px-3 text-sm"
                    defaultValue={`Explain the scope of ${standard.number} in simple terms`}
                  />
                  <Button
                    nativeButton={false}
                    render={<Link href="/ask" />}
                    className="rounded-md"
                  >
                    Ask with evidence <ArrowRight />
                  </Button>
                </div>
              </div>
            </div>
            <aside className="space-y-5">
              <div className="panel p-5">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <CalendarDays className="size-4 text-cyan-300" /> Version
                  register
                </div>
                <dl className="mt-4 space-y-3 text-xs">
                  <Meta label="Version" value={standard.version} />
                  <Meta label="Fixture status" value={standard.status} />
                  <Meta label="Publication date" value="Not verified in demo" />
                  <Meta label="Effective date" value="Not verified in demo" />
                  <Meta label="Last retrieved" value={standard.lastChecked} />
                </dl>
              </div>
              <div className="panel p-5">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <ShieldQuestion className="size-4 text-amber-300" />{' '}
                  Certification intelligence
                </div>
                <p className="mt-3 text-xs leading-5 text-muted-foreground">
                  No mandatory or voluntary status is asserted until a current
                  QCO and certification-scheme record supports it.
                </p>
                <Button
                  nativeButton={false}
                  render={<Link href="/product" />}
                  variant="outline"
                  className="mt-4 w-full rounded-md"
                >
                  Analyse a product
                </Button>
              </div>
            </aside>
          </div>
        </div>
      </section>
    </AppShell>
  );
}

function Relation({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-[#0c0d0e] p-3">
      <div className="text-[9px] tracking-[.1em] text-primary">{label}</div>
      <div className="mt-2 text-xs leading-5 text-muted-foreground">
        {value}
      </div>
    </div>
  );
}
function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 border-b border-border pb-3 last:border-0 last:pb-0">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right text-foreground">{value}</dd>
    </div>
  );
}
