'use client';

import { use } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowRight,
  BookOpenText,
  CalendarDays,
  FileText,
  GitBranch,
  ShieldQuestion,
} from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { ActionLink } from '@/components/manakai/action-link';
import { Badge } from '@/components/ui/badge';
import { ErrorState, LoadingState } from '@/components/manakai/data-state';
import { api, errorMessage } from '@/lib/api-client';

export default function StandardDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const standardQuery = useQuery({ queryKey: ['standard', id], queryFn: () => api.standard(id) });
  const relationshipsQuery = useQuery({ queryKey: ['relationships', id], queryFn: () => api.relationships(id) });
  const labsQuery = useQuery({ queryKey: ['labs'], queryFn: api.labs });
  if (standardQuery.isPending || relationshipsQuery.isPending || labsQuery.isPending) return <AppShell current="/standards"><section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10"><div className="mx-auto max-w-[1180px]"><LoadingState label="Loading standard record…" /></div></section></AppShell>;
  if (standardQuery.isError || relationshipsQuery.isError || labsQuery.isError) return <AppShell current="/standards"><section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10"><div className="mx-auto max-w-[1180px]"><ErrorState message={errorMessage(standardQuery.error ?? relationshipsQuery.error ?? labsQuery.error)} onRetry={() => { void standardQuery.refetch(); void relationshipsQuery.refetch(); void labsQuery.refetch(); }} actionHref="/standards" actionLabel="Back to standards" /></div></section></AppShell>;
  const standard = standardQuery.data;
  const relationships = relationshipsQuery.data;
  const labs = labsQuery.data.filter((lab) => lab.standards.includes(standard.number));
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
                    This page contains {standard.source_kind === 'AUTHORITATIVE' ? 'source-linked official metadata' : standard.source_kind === 'DEMO' ? 'clearly labelled demonstration metadata' : 'limited structured metadata'}. It does not reproduce the complete Indian Standard. Confirm the latest official publication before acting.
                  </p>
                </div>
              </div>
              <div className="panel p-5">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <GitBranch className="size-4 text-primary" /> Regulatory
                  relationships
                </div>
                <div className="mt-5 grid gap-3 sm:grid-cols-3">
                  {relationships.map((relationship) => <Relation key={relationship.id} label={relationship.relationship_type} value={`${relationship.target_standard.number}: ${relationship.target_standard.title}`} />)}
                  <Relation
                    label="CHECK PRODUCT STATUS"
                    value="Analyse a specific product to evaluate the applicable QCO and date"
                  />
                  <Relation label="TESTED_USING" value={`${labs.length} matching lab records`} />
                </div>
              </div>
              <div className="panel p-5">
                <span className="eyebrow">Ask about this standard</span>
                <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"><p className="text-xs leading-5 text-muted-foreground">Open Ask ManakAI with this standard already included in the question.</p><ActionLink href={`/ask?q=${encodeURIComponent(`Explain the scope of ${standard.number} in simple terms`)}`}>Ask with evidence <ArrowRight /></ActionLink></div>
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
                  <Meta label="Record status" value={standard.status} />
                  <Meta label="Publication date" value={standard.publication_date ?? 'Not available'} />
                  <Meta label="Effective date" value={standard.effective_date ?? 'Not available'} />
                  <Meta label="Last retrieved" value={standard.retrieved_at ? new Date(standard.retrieved_at).toLocaleDateString('en-IN') : 'Not recorded'} />
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
                <ActionLink href="/product" variant="outline" className="mt-4 w-full">Analyse a product</ActionLink>
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
