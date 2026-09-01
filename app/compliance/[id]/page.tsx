'use client';

import { use } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import {
  AlertTriangle,
  ArrowRight,
  BookOpenText,
  CheckCircle2,
  Circle,
  CircleAlert,
  ExternalLink,
  FileCheck2,
  FlaskConical,
  ShieldCheck,
} from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ErrorState, LoadingState } from '@/components/manakai/data-state';
import { api, errorMessage } from '@/lib/api-client';

export default function CompliancePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const profileQuery = useQuery({ queryKey: ['compliance', id], queryFn: () => api.compliance(id) });
  const journeyQuery = useQuery({ queryKey: ['journey', id], queryFn: () => api.journey(id) });
  if (profileQuery.isPending || journeyQuery.isPending) return <AppShell current="/compliance"><section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10"><div className="mx-auto max-w-[1180px]"><LoadingState label="Loading compliance profile…" /></div></section></AppShell>;
  if (profileQuery.isError || journeyQuery.isError) return <AppShell current="/compliance"><section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10"><div className="mx-auto max-w-[1180px]"><ErrorState message={errorMessage(profileQuery.error ?? journeyQuery.error)} /></div></section></AppShell>;
  const p = profileQuery.data;
  const standard = p.applicable_standards[0];
  const journeySteps = journeyQuery.data;
  const authoritative = p.data_mode === 'AUTHORITATIVE';
  return (
    <AppShell current="/compliance">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1180px]">
          <PageHeader
            eyebrow="Decide → Act"
            title="Compliance profile"
            description="An auditable interpretation of the product, its candidate standard, known evidence gaps and the next safest actions."
            action={
              <Badge className="bg-emerald-400/10 text-emerald-300">
                {Math.round(p.confidence * 100)}% classification confidence
              </Badge>
            }
          />
          <div className={`mb-5 flex gap-3 rounded-md border p-4 ${authoritative ? 'border-emerald-300/20 bg-emerald-300/5' : 'border-amber-300/20 bg-amber-300/5'}`}>
            {authoritative ? <ShieldCheck className="mt-0.5 size-4 shrink-0 text-emerald-300" /> : <AlertTriangle className="mt-0.5 size-4 shrink-0 text-amber-300" />}
            <div>
              <p className={`text-sm font-medium ${authoritative ? 'text-emerald-100' : 'text-amber-100'}`}>
                {authoritative ? 'Authoritative BIS/government evidence profile' : 'Demo compliance profile — not a legal determination'}
              </p>
              <p className={`mt-1 text-xs leading-5 ${authoritative ? 'text-emerald-100/65' : 'text-amber-100/65'}`}>
                {authoritative ? `Decision evaluated as of ${p.as_of_date}. Confirm missing product attributes before relying on scope applicability.` : 'The standard match is a fixture. The app deliberately withholds a mandatory/voluntary claim until a current authoritative QCO source is connected.'}
              </p>
            </div>
          </div>
          <div className="grid gap-5 xl:grid-cols-[1.15fr_.85fr]">
            <div className="space-y-5">
              <div className="panel overflow-hidden">
                <div className="panel-header">
                  <div>
                    <span className="eyebrow">Product</span>
                    <h2 className="panel-title">{p.product.interpreted_product}</h2>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {p.product.role} · {p.product.category}
                    </p>
                  </div>
                  <ShieldCheck className="size-5 text-primary" />
                </div>
                <div className="grid gap-px bg-border sm:grid-cols-2">
                  <div className="metric">
                    <span>Applicable candidate</span>
                    <strong className="text-lg">{standard.number}</strong>
                    <small>{standard.title}</small>
                  </div>
                  <div className="metric">
                    <span>Certification status</span>
                    <strong className="text-base text-amber-300">
                      {p.mandatory_status}
                    </strong>
                    <small>{p.qco ? `${p.qco.notification_number} · ${p.qco.status}` : 'No QCO record connected'}</small>
                  </div>
                </div>
                <div className="p-5">
                  <div className="eyebrow">Why this applies</div>
                  {p.explanation.length ? <div className="mt-3 space-y-3">{p.explanation.map((node) => <div key={node.question} className="rounded-md border border-border p-3"><p className="text-xs font-medium text-foreground">{node.question}</p><p className="mt-1 text-sm text-primary">{node.conclusion}</p><div className="mt-2 flex flex-wrap gap-2">{node.facts.map((fact) => <Badge key={`${fact.label}-${fact.value}`} variant="outline">{fact.label}: {fact.value ?? 'Unknown'}</Badge>)}</div></div>)}</div> : <p className="mt-2 text-sm leading-6 text-muted-foreground">Product terms align with the stored demo category and scope metadata. Missing attributes must be confirmed before final classification.</p>}
                  <div className="mt-4 flex flex-wrap gap-2">
                    <Button
                      nativeButton={false}
                      render={<Link href={`/standards/${standard.id}`} />}
                      size="sm"
                      className="rounded-md"
                    >
                      View standard <ArrowRight />
                    </Button>
                    <Button
                      nativeButton={false}
                      render={<Link href="/ask" />}
                      size="sm"
                      variant="outline"
                      className="rounded-md"
                    >
                      Ask about this
                    </Button>
                  </div>
                </div>
              </div>
              <div className="grid gap-5 md:grid-cols-2">
                <InfoList
                  icon={<FlaskConical />}
                  title="Required testing"
                  items={p.tests}
                />
                <InfoList
                  icon={<FileCheck2 />}
                  title="Prepare documents"
                  items={p.required_documents}
                />
              </div>
              <div className="panel p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="eyebrow">Evidence register</span>
                    <h2 className="panel-title">Claims and provenance</h2>
                  </div>
                  <BookOpenText className="size-5 text-cyan-300" />
                </div>
                <div className="mt-5 overflow-x-auto">
                  <table className="w-full min-w-[620px] text-left text-xs">
                    <thead className="text-muted-foreground">
                      <tr className="border-b border-border">
                        <th className="pb-3 font-medium">Claim</th>
                        <th className="pb-3 font-medium">Source</th>
                        <th className="pb-3 font-medium">Location</th>
                        <th className="pb-3 font-medium">State</th>
                      </tr>
                    </thead>
                    <tbody>
                      {p.evidence.map((citation) => <EvidenceRow key={citation.id} claim={citation.claim ?? citation.document_title} source={citation.document_identifier ?? citation.standard_number ?? citation.document_type} location={[citation.page ? `p. ${citation.page}` : null, citation.clause ? `cl. ${citation.clause}` : null].filter(Boolean).join(' · ') || citation.document_type} state={citation.status === 'SUPERSEDED' ? 'Superseded' : citation.status === 'UPCOMING' || citation.status === 'NOTIFIED' ? citation.status : citation.source_kind === 'AUTHORITATIVE' ? 'Verified BIS source' : citation.source_kind === 'VERIFIED_DERIVED' ? 'Verified derived' : citation.source_kind === 'DEMO' ? 'Demo data' : 'Unverified'} sourceUrl={citation.source_url} />)}
                      {!authoritative && <EvidenceRow
                        claim="Mandatory certification"
                        source={p.qco?.title ?? 'Current QCO source'}
                        location="Not connected"
                        state="Unverified"
                      />}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            <aside className="space-y-5">
              <div className="panel p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="eyebrow">Journey</span>
                    <h2 className="panel-title">6-stage action plan</h2>
                  </div>
                  <span className="font-heading text-2xl text-primary">
                    33%
                  </span>
                </div>
                <div className="mt-5">
                  {journeySteps.map((step, index) => (
                    <div
                      key={step.title}
                      className="relative flex gap-3 pb-6 last:pb-0"
                    >
                      <div className="relative z-10 grid size-6 shrink-0 place-items-center rounded-full border border-border bg-card">
                        {step.status === 'complete' ? (
                          <CheckCircle2 className="size-4 text-emerald-300" />
                        ) : step.status === 'attention' ? (
                          <CircleAlert className="size-4 text-amber-300" />
                        ) : (
                          <Circle className="size-3 text-muted-foreground" />
                        )}
                      </div>
                      {index < journeySteps.length - 1 && (
                        <span className="absolute left-[11px] top-6 h-full w-px bg-border" />
                      )}
                      <div>
                        <p className="text-sm font-medium">{step.title}</p>
                        <p className="mt-1 text-xs leading-5 text-muted-foreground">
                          {step.explanation}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="panel p-5">
                <span className="eyebrow">Recommended next action</span>
                <h3 className="mt-2 font-heading text-lg tracking-[-.03em]">
                  {authoritative ? (journeySteps.find((step) => step.status !== 'complete')?.title ?? 'Review evidence') : 'Verify the live regulatory record'}
                </h3>
                <p className="mt-2 text-xs leading-5 text-muted-foreground">
                  {authoritative ? 'Resolve warnings, confirm voltage and enterprise category, then contact a currently recognised laboratory for the exact scope.' : 'Connect or consult the current BIS/QCO source, then freeze the verified document version used for the decision.'}
                </p>
                <Button
                  nativeButton={false}
                  render={<Link href="/labs" />}
                  className="mt-4 w-full rounded-md"
                >
                  Find a testing lab <ExternalLink />
                </Button>
              </div>
            </aside>
          </div>
        </div>
      </section>
    </AppShell>
  );
}

function InfoList({
  icon,
  title,
  items,
}: {
  icon: React.ReactNode;
  title: string;
  items: string[];
}) {
  return (
    <div className="panel p-5">
      <div className="flex items-center gap-2 text-sm font-medium text-primary">
        {icon}
        <span className="text-foreground">{title}</span>
      </div>
      <ul className="mt-4 space-y-3">
        {items.map((item) => (
          <li
            key={item}
            className="flex gap-2 text-xs leading-5 text-muted-foreground"
          >
            <CheckCircle2 className="mt-0.5 size-3.5 shrink-0 text-emerald-300" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
function EvidenceRow({
  claim,
  source,
  location,
  state,
  sourceUrl,
}: {
  claim: string;
  source: string;
  location: string;
  state: string;
  sourceUrl?: string | null;
}) {
  return (
    <tr className="border-b border-border last:border-0">
      <td className="py-3 pr-4 text-foreground">{claim}</td>
      <td className="py-3 pr-4 text-muted-foreground">{sourceUrl ? <a className="hover:text-primary" href={sourceUrl} target="_blank" rel="noreferrer">{source} <ExternalLink className="inline size-3" /></a> : source}</td>
      <td className="py-3 pr-4 text-muted-foreground">{location}</td>
      <td className="py-3">
        <Badge
          variant="outline"
          className={
            state === 'Unverified' || state === 'Superseded'
              ? 'border-amber-300/20 text-amber-300'
              : 'text-cyan-300'
          }
        >
          {state}
        </Badge>
      </td>
    </tr>
  );
}
