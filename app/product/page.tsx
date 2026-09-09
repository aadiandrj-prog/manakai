'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useMutation, useQuery } from '@tanstack/react-query';
import { ArrowRight, BookOpenText, CheckCircle2, CircleAlert, HelpCircle, LoaderCircle, Search, ShieldAlert, Sparkles } from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { ActionLink } from '@/components/manakai/action-link';
import { FeedbackWidget } from '@/components/manakai/feedback-widget';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ErrorState } from '@/components/manakai/data-state';
import { api, errorMessage, type ComplianceProfile } from '@/lib/api-client';

const scenarios = [
  'I manufacture a 1500 W electric kettle for household use in India.',
  'I manufacture motorcycle helmets for two-wheeler riders in India.',
  'We produce OPC 53 ordinary Portland cement in India.',
  'I manufacture a 5 litre domestic pressure cooker in India.',
  'I sell 22K916 gold jewellery with HUID.',
];

export default function ProductPage() {
  return <Suspense fallback={<AppShell current="/product"><section className="px-4 py-8"><div className="mx-auto max-w-[1120px]"><div className="panel min-h-56 animate-pulse" /></div></section></AppShell>}><ProductPageContent /></Suspense>;
}

function ProductPageContent() {
  const searchParams = useSearchParams();
  const [description, setDescription] = useState(() => searchParams.get('q') || scenarios[0]);
  const [role, setRole] = useState('Manufacturer');
  const [enterpriseCategory, setEnterpriseCategory] = useState('GENERAL');
  const analysis = useMutation({ mutationFn: api.analyse });
  const coverage = useQuery({ queryKey: ['coverage'], queryFn: api.coverage });
  const profile = analysis.data;
  const suggestions = (coverage.data ?? []).filter((item) => item.aliases?.some((alias) => alias.toLowerCase().includes(description.trim().toLowerCase()) || description.toLowerCase().includes(alias.toLowerCase()))).slice(0, 5);

  useEffect(() => {
    if (!profile || profile.coverage.coverage_status === 'UNSUPPORTED') return;
    window.localStorage.setItem('manakai:last-compliance-profile', JSON.stringify({ id: profile.id, product: profile.product.interpreted_product, status: friendlyStatus(profile), asOfDate: profile.as_of_date }));
  }, [profile]);

  function analyse() {
    if (!description.trim()) return;
    analysis.mutate({ description: description.trim(), role: role.toLowerCase(), language: 'en', enterprise_category: enterpriseCategory });
  }

  return (
    <AppShell current="/product">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1120px]">
          <PageHeader eyebrow="Check my product" title="What BIS requirements may apply?" description="Describe the product in everyday language. Add only the details you know—ManakAI will show what is verified, what is missing, and what to do next." />
          <form className="panel p-5 sm:p-6" onSubmit={(event) => { event.preventDefault(); analyse(); }}>
            <div className="flex items-center gap-2 text-sm font-medium"><Sparkles className="size-4 text-primary" /> Describe your product</div>
            <label htmlFor="description" className="mt-4 block text-xs text-muted-foreground">What do you make, import, sell, or use?</label>
            <textarea id="description" value={description} onChange={(event) => setDescription(event.target.value)} className="mt-2 min-h-28 w-full resize-y rounded-md border border-input bg-[#0b0c0d] p-3 text-sm leading-6 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20" placeholder="For example: I manufacture a 1500 W, 230 V household electric kettle in India" />
            {suggestions.length > 0 && <div className="mt-2 flex flex-wrap items-center gap-2"><span className="text-[10px] uppercase tracking-[.1em] text-muted-foreground">Published matches</span>{suggestions.map((item) => <button key={item.id} type="button" onClick={() => setDescription(`I manufacture ${item.category_name} in India`)} className="rounded border border-primary/20 bg-primary/5 px-2 py-1 text-[10px] text-primary">{item.category_name}</button>)}</div>}
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <label className="text-xs text-muted-foreground">Your role<select aria-label="Your role" value={role} onChange={(event) => setRole(event.target.value)} className="mt-2 h-11 w-full rounded-md border border-input bg-[#0b0c0d] px-3 text-sm text-foreground"><option>Manufacturer</option><option>Importer</option><option>Seller</option><option>Consumer</option></select></label>
              <label className="text-xs text-muted-foreground">Business size for implementation dates<select aria-label="Business size for implementation dates" value={enterpriseCategory} onChange={(event) => setEnterpriseCategory(event.target.value)} className="mt-2 h-11 w-full rounded-md border border-input bg-[#0b0c0d] px-3 text-sm text-foreground"><option value="GENERAL">General / not sure</option><option value="SMALL">Small enterprise</option><option value="MICRO">Micro enterprise</option></select></label>
            </div>
            <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"><p className="text-xs leading-5 text-muted-foreground">You can correct the description and run the check again at any time.</p><Button type="submit" disabled={!description.trim() || analysis.isPending} className="min-h-11 rounded-md px-6">{analysis.isPending ? <><LoaderCircle className="animate-spin" /> Checking regulatory records…</> : <><Search /> Check requirements</>}</Button></div>
            <details className="mt-5 border-t border-border pt-4"><summary className="cursor-pointer text-xs font-medium text-primary">Use an example product</summary><div className="mt-3 flex flex-wrap gap-2">{scenarios.map((item) => <button type="button" key={item} onClick={() => setDescription(item)} className="min-h-10 rounded border border-border px-3 py-2 text-left text-[11px] leading-4 text-muted-foreground hover:bg-muted">{item}</button>)}</div></details>
          </form>

          <div className="mt-5" aria-live="polite">
            {analysis.isPending && <div className="panel flex min-h-40 items-center justify-center px-5 text-center"><div><LoaderCircle className="mx-auto size-6 animate-spin text-primary" /><p className="mt-3 text-sm">Checking product coverage and current dates…</p><p className="mt-2 text-xs text-muted-foreground">If free staging is waking up, this may take up to a minute.</p></div></div>}
            {analysis.isError && <ErrorState message={errorMessage(analysis.error)} onRetry={analyse} />}
            {profile && !analysis.isPending && (profile.coverage.coverage_status === 'UNSUPPORTED' ? <UnsupportedResult profile={profile} /> : <SupportedResult profile={profile} />)}
          </div>
        </div>
      </section>
    </AppShell>
  );
}

function SupportedResult({ profile }: { profile: ComplianceProfile }) {
  const standard = profile.applicable_standards[0];
  const partial = profile.coverage.coverage_status === 'PARTIAL';
  const demo = profile.data_mode === 'DEMO';
  const nextAction = profile.next_steps.find((step) => step.status !== 'complete')?.next_action || profile.next_steps.find((step) => step.status !== 'complete')?.title || 'Review the evidence and confirm any missing product details.';
  const confirmationItems = [...new Set([...profile.coverage.known_limitations, ...profile.warnings])].slice(0, 6);
  return <section className="space-y-5" aria-labelledby="result-title">
    <div className="panel overflow-hidden">
      <div className="panel-header"><div><span className="eyebrow">Product identified</span><h2 id="result-title" className="panel-title">{profile.product.interpreted_product}</h2><p className="mt-1 text-xs text-muted-foreground">Checked for {profile.product.role} · {formatDate(profile.as_of_date)}</p></div><Badge className={demo || partial ? 'bg-amber-300/10 text-amber-300' : 'bg-emerald-400/10 text-emerald-300'}>{demo ? 'Demo data' : partial ? 'Partial coverage' : 'Verified coverage'}</Badge></div>
      <div className="grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-4">
        <ResultFact label="What?" value={standard ? `${standard.number}:${standard.version}` : 'Unable to verify'} detail={standard?.title ?? 'No verified standard mapping'} />
        <ResultFact label="Status?" value={friendlyStatus(profile)} detail={profile.qco?.notification_number ?? 'No applicable order verified'} tone="amber" />
        <ResultFact label="When?" value={profile.qco?.effective_from ? formatDate(profile.qco.effective_from) : 'Date not verified'} detail={`Status on ${formatDate(profile.as_of_date)}`} />
        <ResultFact label="Action?" value="Review next step" detail={nextAction} tone="primary" />
      </div>
      <div className="p-5"><p className="text-sm leading-6 text-muted-foreground">{profile.coverage.coverage_reason}</p><div className="mt-5 flex flex-wrap gap-2"><ActionLink href={`/compliance/${profile.id}`}>Open action plan <ArrowRight /></ActionLink>{standard && <ActionLink variant="outline" href={`/standards/${standard.id}`}>View standard</ActionLink>}<ActionLink variant="outline" href={`/ask?q=${encodeURIComponent(`Explain the requirements for ${profile.product.interpreted_product}`)}`}>Ask about this result</ActionLink></div></div>
    </div>
    {(partial || confirmationItems.length > 0) && <div className="grid gap-4 md:grid-cols-2"><div className="rounded-md border border-emerald-300/20 bg-emerald-300/5 p-4"><div className="flex items-center gap-2 text-sm font-medium text-emerald-100"><CheckCircle2 className="size-4 text-emerald-300" /> What we could verify</div><ul className="mt-3 space-y-2 text-xs leading-5 text-emerald-50/70"><li>{standard ? `Applicable standard: ${standard.number}:${standard.version}` : 'Available product metadata'}</li>{profile.qco && <li>Regulatory instrument and status for the selected date</li>}<li>{profile.evidence.length} linked evidence record{profile.evidence.length === 1 ? '' : 's'}</li></ul></div><div className="rounded-md border border-amber-300/20 bg-amber-300/5 p-4"><div className="flex items-center gap-2 text-sm font-medium text-amber-100"><CircleAlert className="size-4 text-amber-300" /> Still needs confirmation</div><ul className="mt-3 space-y-2 text-xs leading-5 text-amber-50/70">{confirmationItems.map((item) => <li key={item}>• {item}</li>)}</ul></div></div>}
    <details className="panel group p-5"><summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-3 text-sm font-medium"><span className="flex items-center gap-2"><BookOpenText className="size-4 text-primary" /> Why this result?</span><span className="text-xs text-muted-foreground group-open:hidden">Show details</span></summary><div className="mt-4 space-y-3 border-t border-border pt-4">{profile.explanation.map((node) => <article key={node.question} className="rounded-md border border-border p-3"><p className="text-xs font-medium">{node.question}</p><p className="mt-1 text-sm text-primary">{node.conclusion}</p></article>)}{!profile.explanation.length && <p className="text-xs text-muted-foreground">The result is based on the stored product-category mapping and the regulatory records available for the selected date.</p>}</div></details>
    <div className="flex justify-end"><FeedbackWidget context={`${profile.coverage.category_slug} · ${profile.coverage.coverage_status}`} /></div>
  </section>;
}

function UnsupportedResult({ profile }: { profile: ComplianceProfile }) {
  return <section className="panel p-5 sm:p-7" aria-labelledby="unsupported-title"><div className="flex gap-3"><ShieldAlert className="mt-1 size-6 shrink-0 text-amber-300" /><div><span className="eyebrow">Coverage not available yet</span><h2 id="unsupported-title" className="mt-2 font-heading text-xl">We can’t verify an end-to-end BIS result for this product</h2><p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">{profile.coverage.coverage_reason} ManakAI will not guess a standard, certification requirement, or effective date from general AI knowledge.</p></div></div>{profile.related_standard_metadata.length > 0 && <div className="mt-5 rounded-md border border-cyan-300/20 bg-cyan-300/5 p-4"><p className="text-sm font-medium text-cyan-100">Related standards metadata — not an applicability decision</p><ul className="mt-3 space-y-2 text-xs text-cyan-50/70">{profile.related_standard_metadata.map((item) => <li key={item.id}>{item.number}:{item.version} — {item.title}</li>)}</ul></div>}<div className="mt-5 rounded-md border border-border bg-[#0c0d0e] p-4"><div className="flex items-center gap-2 text-sm font-medium"><HelpCircle className="size-4 text-primary" /> What you can do</div><ul className="mt-3 space-y-2 text-xs leading-5 text-muted-foreground"><li>Search the standards metadata currently available in ManakAI.</li><li>Check the official BIS product-certification and standards search services.</li><li>Ask a qualified compliance professional to confirm the current product scope.</li></ul></div><div className="mt-5 flex flex-wrap gap-2"><ActionLink href="/coverage">Browse published coverage</ActionLink><ActionLink variant="outline" href="/standards">Search standards metadata</ActionLink><ActionLink variant="outline" href="/product">Try another description</ActionLink></div><div className="mt-5"><FeedbackWidget context="unsupported product" /></div></section>;
}

function ResultFact({ label, value, detail, tone }: { label: string; value: string; detail: string; tone?: 'amber' | 'primary' }) {
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
