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
          <div className="mb-5 flex gap-3 rounded-md border border-amber-300/20 bg-amber-300/5 p-4">
            <AlertTriangle className="mt-0.5 size-4 shrink-0 text-amber-300" />
            <div>
              <p className="text-sm font-medium text-amber-100">
                Demo compliance profile — not a legal determination
              </p>
              <p className="mt-1 text-xs leading-5 text-amber-100/65">
                The standard match is a fixture. The app deliberately withholds
                a mandatory/voluntary claim until a current authoritative QCO
                source is connected.
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
                    <small>{p.qco ?? 'No QCO record connected'}</small>
                  </div>
                </div>
                <div className="p-5">
                  <div className="eyebrow">Why this applies</div>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    The product is interpreted as a self-contained rechargeable
                    emergency luminaire. Its intended emergency-lighting
                    function matches the seeded scope metadata for{' '}
                    {standard.number}. Voltage, installation type and battery
                    details should be confirmed before final classification.
                  </p>
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
                      {p.evidence.map((citation) => <EvidenceRow key={citation.id} claim={citation.document_title} source={citation.standard_number ?? citation.document_type} location={citation.clause ?? citation.document_type} state={citation.source_kind === 'verified' ? 'Verified' : 'Fixture'} />)}
                      <EvidenceRow
                        claim="Mandatory certification"
                        source={p.qco ?? 'Current QCO source'}
                        location="Not connected"
                        state="Unverified"
                      />
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
                  Verify the live regulatory record
                </h3>
                <p className="mt-2 text-xs leading-5 text-muted-foreground">
                  Connect or consult the current BIS/QCO source, then freeze the
                  verified document version used for the decision.
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
}: {
  claim: string;
  source: string;
  location: string;
  state: string;
}) {
  return (
    <tr className="border-b border-border last:border-0">
      <td className="py-3 pr-4 text-foreground">{claim}</td>
      <td className="py-3 pr-4 text-muted-foreground">{source}</td>
      <td className="py-3 pr-4 text-muted-foreground">{location}</td>
      <td className="py-3">
        <Badge
          variant="outline"
          className={
            state === 'Unverified'
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
