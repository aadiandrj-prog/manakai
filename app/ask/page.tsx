'use client';

import { Suspense, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { ArrowRight, BookOpenText, Bot, CheckCircle2, CircleAlert, FlaskConical, Languages, LoaderCircle, MessageSquareText, RotateCcw, ShieldCheck } from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select';
import { ErrorState } from '@/components/manakai/data-state';
import { FeedbackWidget } from '@/components/manakai/feedback-widget';
import { api, errorMessage, type ConversationResponse } from '@/lib/api-client';

const starters = [
  'I manufacture a 1500W 230V electric kettle for household use.',
  'I manufacture motorcycle helmets for two-wheeler riders in India.',
  'We produce OPC 53 ordinary Portland cement in India.',
  'I manufacture a 5 litre domestic pressure cooker in India.',
  'How should a consumer verify the HUID on 22K916 gold jewellery?',
];

export default function AskPage() {
  return <Suspense fallback={<AppShell current="/ask"><section className="px-4 py-8"><div className="mx-auto max-w-[1100px]"><div className="panel min-h-56 animate-pulse" /></div></section></AppShell>}><AskPageContent /></Suspense>;
}

function AskPageContent() {
  const searchParams = useSearchParams();
  const [question, setQuestion] = useState(() => searchParams.get('q') || starters[0]);
  const [language, setLanguage] = useState('auto');
  const [conversation, setConversation] = useState<ConversationResponse | null>(null);
  const mutation = useMutation({
    mutationFn: async (message: string) => conversation
      ? api.conversationMessage(conversation.conversation_id, message, language)
      : api.chat(message, language),
    onSuccess: (data) => { setConversation(data); setQuestion(''); },
  });
  function send() {
    const message = question.trim();
    if (message) mutation.mutate(message);
  }
  return (
    <AppShell current="/ask">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1100px]">
          <PageHeader eyebrow="Ask with evidence" title="Ask ManakAI" description="Ask about a covered product or standard. ManakAI answers from its regulatory records and shows whether Gemini or a rules-based fallback produced the final wording." />
          <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_280px]">
            <div className="space-y-5">
              {conversation?.messages.length ? (
                <div className="panel max-h-[430px] space-y-3 overflow-y-auto p-4" aria-live="polite">
                  {conversation.messages.map((message) => (
                    <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[88%] rounded-md border p-3 text-sm leading-6 ${message.role === 'user' ? 'border-primary/30 bg-primary/10' : 'border-border bg-[#0c0d0e]'}`}>
                        <div className="mb-1 flex items-center gap-2 text-[10px] uppercase tracking-[.15em] text-muted-foreground">{message.role === 'user' ? <MessageSquareText className="size-3" /> : <Bot className="size-3 text-cyan-300" />}{message.role === 'user' ? 'You' : 'ManakAI'} · {message.language}</div>
                        {message.content}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="panel p-5">
                  <div className="flex items-center gap-2 text-sm font-medium"><ShieldCheck className="size-4 text-cyan-300" /> Start with a published coverage vertical</div>
                  <div className="mt-4 grid gap-2">{starters.map((item) => <button key={item} onClick={() => setQuestion(item)} className="rounded-md border border-border bg-[#0c0d0e] p-3 text-left text-xs leading-5 text-muted-foreground transition hover:border-primary/40 hover:text-foreground">{item}</button>)}</div>
                </div>
              )}
              <div className="analysis-box">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <label htmlFor="question" className="flex items-center gap-2 text-sm font-medium"><MessageSquareText className="size-4 text-primary" /> {conversation ? 'Continue this compliance analysis' : 'Describe the product or ask about evidence'}</label>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground"><Languages className="size-3.5" /><NativeSelect aria-label="Response language" size="sm" value={language} onChange={(event) => setLanguage(event.target.value)}><NativeSelectOption value="auto">Detect language</NativeSelectOption><NativeSelectOption value="en">English</NativeSelectOption><NativeSelectOption value="hi">Hindi</NativeSelectOption><NativeSelectOption value="hinglish">Hinglish</NativeSelectOption></NativeSelect></div>
                </div>
                <textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); send(); } }} placeholder={conversation?.clarification_required ? 'Answer the requested product detail' : 'Ask about a covered product, standard, testing, certification or hallmarking…'} className="mt-4 min-h-24 w-full resize-none rounded-md border border-input bg-[#0b0c0d] p-3 text-sm leading-6 outline-none focus:border-primary" />
                <div className="mt-3 flex items-center justify-between gap-3">
                  <p className="text-[11px] text-muted-foreground">A successful response does not necessarily mean Gemini answered. Check the answer-source card.</p>
                  <div className="flex gap-2">{conversation && <Button variant="outline" size="sm" onClick={() => { setConversation(null); setQuestion(starters[0]); }}><RotateCcw /> New analysis</Button>}<Button onClick={send} disabled={mutation.isPending || !question.trim()} className="rounded-md">{mutation.isPending ? <><LoaderCircle className="animate-spin" /> Analysing</> : <>Send <ArrowRight /></>}</Button></div>
                </div>
              </div>
              {mutation.isError && <ErrorState message={errorMessage(mutation.error)} />}
            </div>
            <aside className="space-y-4">
              <div className="panel p-4"><div className="flex items-center gap-2 text-sm font-medium"><ShieldCheck className="size-4 text-cyan-300" /> What AI can do</div><p className="mt-3 text-xs leading-5 text-muted-foreground">AI may interpret, translate, and explain. Stored evidence and date-aware rules—not model memory—select standards, QCO status, and laboratories.</p></div>
              {conversation && <div className="panel p-4 text-xs" aria-live="polite"><div className="eyebrow">Answer source</div><div className="mt-3 flex flex-wrap gap-2"><Badge variant="outline">{conversation.intent.replaceAll('_', ' ')}</Badge><Badge variant="outline">{conversation.language}</Badge><Badge className={conversation.used_fallback ? 'bg-amber-300/10 text-amber-300' : 'bg-cyan-300/10 text-cyan-300'}>{conversation.used_fallback ? 'Rules-based fallback' : `AI explanation · ${conversation.provider}`}</Badge></div><p className="mt-3 leading-5 text-muted-foreground">{conversation.used_fallback ? 'Gemini was not needed, was unavailable, or its response did not pass validation. The final wording came from a deterministic template built from the regulatory result.' : 'Gemini produced the final wording and it passed identifier, status, and evidence checks. This validates consistency—not usefulness or completeness.'}</p>{conversation.clarification_required && <div className="mt-3 rounded-md border border-amber-300/20 bg-amber-300/5 p-3 text-amber-100"><CircleAlert className="mb-2 size-4" />More information needed: {conversation.unresolved_attributes.join(', ')}</div>}</div>}
            </aside>
          </div>
          {conversation?.compliance_profile && <ComplianceCards response={conversation} />}
          {conversation && conversation.warnings.length > 0 && <div className="mt-5 panel p-5"><div className="flex items-center gap-2 text-sm font-medium"><CircleAlert className="size-4 text-amber-300" /> Warnings</div><div className="mt-3 grid gap-2 sm:grid-cols-2">{conversation.warnings.map((warning) => <div key={warning} className="rounded-md border border-border bg-[#0c0d0e] p-3 text-xs leading-5 text-muted-foreground">{warning}</div>)}</div></div>}
          {conversation && <EvidenceCards response={conversation} />}
          {conversation && <div className="mt-5 flex justify-end"><FeedbackWidget context={`${conversation.intent} · ${conversation.provider} · fallback=${conversation.used_fallback}`} /></div>}
        </div>
      </section>
    </AppShell>
  );
}

function ComplianceCards({ response }: { response: ConversationResponse }) {
  const profile = response.compliance_profile!;
  return <div className="mt-5 grid gap-4 md:grid-cols-3">
    <div className="panel p-4"><div className="flex items-center gap-2 text-xs uppercase tracking-[.14em] text-muted-foreground"><BookOpenText className="size-4 text-primary" /> Coverage & standards</div><div className="mt-3 flex flex-wrap gap-2"><Badge className={profile.data_mode === 'DEMO' || profile.coverage.coverage_status !== 'VERIFIED' ? 'bg-amber-300/10 text-amber-300' : 'bg-emerald-400/10 text-emerald-300'}>{profile.data_mode === 'DEMO' ? 'Demo data' : profile.coverage.coverage_status === 'VERIFIED' ? 'Verified coverage' : 'Partial coverage'}</Badge>{profile.regulatory_regime && <Badge variant="outline">{profile.regulatory_regime.name}</Badge>}</div><div className="mt-3 space-y-2">{profile.applicable_standards.map((standard) => <div key={standard.id}><p className="text-sm font-medium">{standard.number}:{standard.version}</p><p className="text-xs text-muted-foreground">{standard.title}</p></div>)}{!profile.applicable_standards.length && <p className="text-xs leading-5 text-muted-foreground">{profile.coverage.coverage_reason}</p>}</div></div>
    <div className="panel p-4"><div className="flex items-center gap-2 text-xs uppercase tracking-[.14em] text-muted-foreground"><ShieldCheck className="size-4 text-cyan-300" /> Regulatory status</div><p className="mt-3 text-xl font-semibold">{profile.qco?.status ?? profile.mandatory_status}</p><p className="mt-1 text-xs text-muted-foreground">{profile.qco?.notification_number} · {profile.qco?.effective_from ?? 'date unavailable'}</p><p className="mt-3 text-xs">{profile.certification_scheme}</p></div>
    <div className="panel p-4"><div className="flex items-center gap-2 text-xs uppercase tracking-[.14em] text-muted-foreground"><FlaskConical className="size-4 text-amber-300" /> Recognised labs</div><p className="mt-3 text-xl font-semibold">{profile.laboratories.length}</p><div className="mt-2 space-y-1 text-xs text-muted-foreground">{profile.laboratories.slice(0, 3).map((lab) => <p key={lab.id}>{lab.name}</p>)}</div></div>
  </div>;
}

function EvidenceCards({ response }: { response: ConversationResponse }) {
  if (!response.evidence.length) return null;
  return <div className="mt-5 panel p-5"><div className="flex items-center gap-2 text-sm font-medium"><BookOpenText className="size-4 text-primary" /> Authoritative evidence</div><div className="mt-4 grid gap-3 md:grid-cols-2">{response.evidence.map(({ evidence_id, citation }) => <div key={evidence_id} className="rounded-md border border-border bg-[#0c0d0e] p-4"><div className="flex items-start justify-between gap-3"><p className="text-sm font-medium">{citation.document_title}</p><Badge className="bg-cyan-300/10 text-cyan-300">{evidence_id}</Badge></div><p className="mt-2 text-xs leading-5 text-muted-foreground">{citation.standard_number ?? citation.document_type}{citation.clause ? ` · Clause ${citation.clause}` : ''}{citation.page ? ` · Page ${citation.page}` : ''}</p>{citation.source_url && <a href={citation.source_url} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1 text-xs text-primary hover:underline">View official source <ArrowRight className="size-3" /></a>}<div className="mt-3 flex items-center gap-1 text-[10px] text-cyan-300"><CheckCircle2 className="size-3" /> {citation.validation_status}</div></div>)}</div></div>;
}
