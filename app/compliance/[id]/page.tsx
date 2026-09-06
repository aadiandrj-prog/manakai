'use client';

import { use, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, BookOpenText, CheckCircle2, Circle, CircleAlert, ExternalLink, FileCheck2, FlaskConical, ShieldCheck } from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { ActionLink } from '@/components/manakai/action-link';
import { FeedbackWidget } from '@/components/manakai/feedback-widget';
import { Badge } from '@/components/ui/badge';
import { ErrorState, LoadingState } from '@/components/manakai/data-state';
import { api, errorMessage, type ComplianceProfile, type JourneyStep } from '@/lib/api-client';

export default function CompliancePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const profileQuery = useQuery({ queryKey: ['compliance', id], queryFn: () => api.compliance(id) });
  const journeyQuery = useQuery({ queryKey: ['journey', id], queryFn: () => api.journey(id) });
  const profile = profileQuery.data;
  useEffect(() => {
    if (!profile) return;
    window.localStorage.setItem('manakai:last-compliance-profile', JSON.stringify({ id: profile.id, product: profile.product.interpreted_product, status: friendlyStatus(profile), asOfDate: profile.as_of_date }));
  }, [profile]);

  if (profileQuery.isPending || journeyQuery.isPending) return <AppShell current="/compliance"><section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10"><div className="mx-auto max-w-[1120px]"><LoadingState label="Loading your compliance result…" /></div></section></AppShell>;
  if (profileQuery.isError || journeyQuery.isError) return <AppShell current="/compliance"><section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10"><div className="mx-auto max-w-[1120px]"><ErrorState message={errorMessage(profileQuery.error ?? journeyQuery.error)} onRetry={() => { void profileQuery.refetch(); void journeyQuery.refetch(); }} actionHref="/product" actionLabel="Analyse a product" /></div></section></AppShell>;

  const p = profileQuery.data;
  const steps = journeyQuery.data;
  const standard = p.applicable_standards[0];
  const nextStep = steps.find((step) => step.status !== 'complete');
  const completed = steps.filter((step) => step.status === 'complete').length;
  const progress = steps.length ? Math.round((completed / steps.length) * 100) : 0;
  const partial = p.coverage.coverage_status === 'PARTIAL';
  const demo = p.data_mode === 'DEMO';

  return (
    <AppShell current="/compliance">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1120px]">
          <PageHeader eyebrow="Your compliance result" title={p.product.interpreted_product} description={`Status evaluated on ${formatDate(p.as_of_date)} using the product details and evidence currently available.`} action={<Badge className={demo || partial ? 'bg-amber-300/10 text-amber-300' : 'bg-emerald-400/10 text-emerald-300'}>{demo ? 'Demo data' : partial ? 'Partial coverage' : 'Verified coverage'}</Badge>} />

          <section className="panel overflow-hidden" aria-labelledby="result-summary">
            <div className="panel-header"><div><span className="eyebrow">Answer first</span><h2 id="result-summary" className="panel-title">What applies and what should you do?</h2></div><ShieldCheck className="size-5 text-primary" /></div>
            <div className="grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-4">
              <Summary label="What?" value={standard ? `${standard.number}:${standard.version}` : 'Unable to verify'} detail={standard?.title ?? 'No standard was selected'} />
              <Summary label="Status?" value={friendlyStatus(p)} detail={p.qco?.notification_number ?? 'No current order verified'} tone="amber" />
              <Summary label="When?" value={p.qco?.effective_from ? formatDate(p.qco.effective_from) : 'Date not verified'} detail={`Checked on ${formatDate(p.as_of_date)}`} />
              <Summary label="Action?" value={nextStep?.title ?? 'Review complete'} detail={nextStep?.next_action ?? nextStep?.explanation ?? 'Keep the evidence with your decision record.'} tone="primary" />
            </div>
            <div className="p-5"><p className="text-sm leading-6 text-muted-foreground">{p.coverage.coverage_reason}</p>{p.warnings.length > 0 && <div className="mt-4 flex gap-3 rounded-md border border-amber-300/20 bg-amber-300/5 p-3"><CircleAlert className="mt-0.5 size-4 shrink-0 text-amber-300" /><div><p className="text-xs font-medium text-amber-100">Confirm before acting</p><ul className="mt-2 space-y-1 text-xs leading-5 text-amber-50/70">{p.warnings.slice(0, 4).map((warning) => <li key={warning}>• {warning}</li>)}</ul></div></div>}</div>
          </section>

          <div className="mt-5 grid gap-5 lg:grid-cols-[1.12fr_.88fr]">
            <section className="panel p-5" aria-labelledby="journey-heading">
              <div className="flex items-start justify-between gap-4"><div><span className="eyebrow">Action plan</span><h2 id="journey-heading" className="panel-title">{steps.length}-step compliance journey</h2><p className="mt-1 text-xs text-muted-foreground">Each step explains what it means and the next practical action.</p></div><span className="font-heading text-2xl text-primary" aria-label={`${progress} percent complete`}>{progress}%</span></div>
              <div className="mt-6">{steps.map((step, index) => <JourneyItem key={`${step.title}-${index}`} step={step} last={index === steps.length - 1} />)}</div>
            </section>
            <aside className="space-y-5">
              <div className="panel p-5"><span className="eyebrow">Do this next</span><h2 className="mt-2 font-heading text-lg tracking-[-.03em]">{nextStep?.title ?? 'Keep this result for your records'}</h2><p className="mt-2 text-xs leading-5 text-muted-foreground">{nextStep?.next_action ?? nextStep?.explanation ?? 'Review the sources again before a future production or certification decision.'}</p><div className="mt-4 flex flex-col gap-2">{p.laboratories.length > 0 && <ActionLink href="/labs">Find a testing lab <ArrowRight /></ActionLink>}<ActionLink variant="outline" href={`/ask?q=${encodeURIComponent(`Explain the next compliance step for ${p.product.interpreted_product}`)}`}>Ask about this result</ActionLink></div></div>
              {partial && <div className="rounded-md border border-amber-300/20 bg-amber-300/5 p-4"><div className="flex items-center gap-2 text-sm font-medium text-amber-100"><CircleAlert className="size-4 text-amber-300" /> Not fully verified</div><ul className="mt-3 space-y-2 text-xs leading-5 text-amber-50/70">{p.coverage.known_limitations.map((item) => <li key={item}>• {item}</li>)}</ul></div>}
            </aside>
          </div>

          <div className="mt-5 space-y-3">
            <Disclosure icon={<BookOpenText />} title="Why does this apply?" summary="See the structured reasoning behind the product and regulatory status.">{p.explanation.length ? <div className="grid gap-3 md:grid-cols-2">{p.explanation.map((node) => <article key={node.question} className="rounded-md border border-border bg-[#0c0d0e] p-4"><p className="text-xs font-medium">{node.question}</p><p className="mt-2 text-sm text-primary">{node.conclusion}</p><div className="mt-3 flex flex-wrap gap-2">{node.facts.map((fact) => <Badge key={`${fact.label}-${fact.value}`} variant="outline">{fact.label}: {fact.value ?? 'Unknown'}</Badge>)}</div></article>)}</div> : <p className="text-xs text-muted-foreground">No additional explanation nodes were stored for this profile.</p>}</Disclosure>
            <Disclosure icon={<FileCheck2 />} title="View regulatory basis" summary="Standards, QCO, certification route, testing and document preparation."><div className="grid gap-4 md:grid-cols-2"><InfoList title="Applicable standards" items={p.applicable_standards.map((item) => `${item.number}:${item.version} — ${item.title}`)} /><InfoList title="Certification and order" items={[p.certification_scheme || 'Certification route not verified', p.qco ? `${p.qco.notification_number ?? p.qco.title} — ${p.qco.status}` : 'No QCO or order verified']} /><InfoList title="Testing to review" items={p.tests} /><InfoList title="Documents to prepare" items={p.required_documents} /></div></Disclosure>
            <Disclosure icon={<FlaskConical />} title="Testing services" summary={`${p.laboratories.length} laboratory scope record${p.laboratories.length === 1 ? '' : 's'} available for this result.`}>{p.laboratories.length ? <div className="grid gap-3 md:grid-cols-2">{p.laboratories.map((lab) => <article key={lab.id} className="rounded-md border border-border bg-[#0c0d0e] p-4"><h3 className="text-sm font-medium">{lab.name}</h3><p className="mt-2 text-xs text-muted-foreground">{[lab.city, lab.state].filter(Boolean).join(', ')} · {lab.recognition_status}</p>{lab.warning && <p className="mt-2 text-xs text-amber-300">{lab.warning}</p>}{lab.source_url && <a href={lab.source_url} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1 text-xs text-primary">View BIS LIMS scope <ExternalLink className="size-3" /></a>}</article>)}</div> : <p className="text-xs text-muted-foreground">No currently usable laboratory scope is stored for this product and date. Confirm through BIS LIMS.</p>}</Disclosure>
            <Disclosure icon={<BookOpenText />} title="View BIS sources" summary={`${p.evidence.length} evidence record${p.evidence.length === 1 ? '' : 's'} with provenance and source links.`}><div className="grid gap-3 md:grid-cols-2">{p.evidence.map((citation) => <article key={citation.id} className="rounded-md border border-border bg-[#0c0d0e] p-4"><div className="flex items-start justify-between gap-3"><h3 className="text-sm font-medium">{citation.document_title}</h3><Badge variant="outline">{citation.source_kind === 'AUTHORITATIVE' ? 'Official source' : citation.source_kind}</Badge></div><p className="mt-2 text-xs leading-5 text-muted-foreground">{citation.document_identifier ?? citation.standard_number ?? citation.document_type}{citation.clause ? ` · Clause ${citation.clause}` : ''}{citation.page ? ` · Page ${citation.page}` : ''}</p><p className="mt-2 text-[10px] text-muted-foreground">Retrieved {citation.retrieved_at ? new Date(citation.retrieved_at).toLocaleDateString('en-IN') : 'date unavailable'} · {citation.validation_status}</p>{citation.source_url && <a href={citation.source_url} target="_blank" rel="noreferrer" className="mt-3 inline-flex min-h-10 items-center gap-1 text-xs text-primary">Open official source <ExternalLink className="size-3" /></a>}</article>)}</div></Disclosure>
          </div>
          <div className="mt-5 flex justify-end"><FeedbackWidget context={`${p.id} · ${p.coverage.coverage_status}`} /></div>
        </div>
      </section>
    </AppShell>
  );
}

function JourneyItem({ step, last }: { step: JourneyStep; last: boolean }) {
  const complete = step.status === 'complete';
  const attention = step.status === 'attention' || step.status === 'required';
  return <article className="relative flex gap-3 pb-6 last:pb-0"><div className="relative z-10 grid size-7 shrink-0 place-items-center rounded-full border border-border bg-card">{complete ? <CheckCircle2 className="size-4 text-emerald-300" /> : attention ? <CircleAlert className="size-4 text-amber-300" /> : <Circle className="size-3 text-muted-foreground" />}</div>{!last && <span className="absolute left-[13px] top-7 h-full w-px bg-border" />}<div className="min-w-0"><div className="flex flex-wrap items-center gap-2"><h3 className="text-sm font-medium">{step.title}</h3><Badge variant="outline">{complete ? 'Completed' : attention ? 'Needs attention' : step.status.replaceAll('_', ' ')}</Badge></div><p className="mt-1 text-xs leading-5 text-muted-foreground">{step.explanation}</p>{step.next_action && <div className="mt-2 rounded-md border border-primary/20 bg-primary/5 p-2 text-xs leading-5 text-primary"><strong>Next action:</strong> {step.next_action}</div>}</div></article>;
}

function Disclosure({ icon, title, summary, children }: { icon: React.ReactNode; title: string; summary: string; children: React.ReactNode }) {
  return <details className="panel group p-5"><summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-4"><span className="flex items-center gap-2 text-sm font-medium text-foreground"><span className="text-primary">{icon}</span>{title}</span><span className="text-right text-xs text-muted-foreground group-open:hidden">{summary}</span></summary><div className="mt-4 border-t border-border pt-4">{children}</div></details>;
}

function InfoList({ title, items }: { title: string; items: string[] }) {
  return <div><h3 className="text-xs font-medium uppercase tracking-[.1em] text-primary">{title}</h3><ul className="mt-3 space-y-2 text-xs leading-5 text-muted-foreground">{items.length ? items.map((item) => <li key={item}>• {item}</li>) : <li>No verified information stored.</li>}</ul></div>;
}

function Summary({ label, value, detail, tone }: { label: string; value: string; detail: string; tone?: 'amber' | 'primary' }) {
  return <div className="metric min-h-36"><span>{label}</span><strong className={`text-base ${tone === 'amber' ? 'text-amber-300' : tone === 'primary' ? 'text-primary' : ''}`}>{value}</strong><small className="line-clamp-3">{detail}</small></div>;
}

function friendlyStatus(profile: ComplianceProfile) {
  const value = profile.qco?.status ?? profile.mandatory_status;
  const labels: Record<string, string> = { ACTIVE: 'Mandatory now', UPCOMING: 'Upcoming requirement', NOTIFIED: 'Notified', VOLUNTARY: 'Voluntary', UNKNOWN: 'Unable to verify', UNVERIFIED: 'Unable to verify' };
  return labels[value] ?? value.replaceAll('_', ' ').toLowerCase().replace(/^./, (letter) => letter.toUpperCase());
}

function formatDate(value: string) {
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' });
}
