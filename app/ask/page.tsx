'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import {
  ArrowRight,
  BookOpenText,
  CheckCircle2,
  CircleAlert,
  LoaderCircle,
  Search,
} from 'lucide-react';
import { AppShell, PageHeader } from '@/components/manakai/app-shell';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ErrorState, LoadingState } from '@/components/manakai/data-state';
import { api, errorMessage } from '@/lib/api-client';

export default function AskPage() {
  const [question, setQuestion] = useState(
    'What tests are relevant to a rechargeable emergency luminaire?',
  );
  const [submitted, setSubmitted] = useState(question);
  const answerQuery = useQuery({ queryKey: ['qa', submitted], queryFn: () => api.ask(submitted), enabled: Boolean(submitted) });
  function ask() {
    setSubmitted(question.trim());
  }
  return (
    <AppShell current="/ask">
      <section className="px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <div className="mx-auto max-w-[1000px]">
          <PageHeader
            eyebrow="Evidence Q&A"
            title="Ask ManakAI"
            description="Questions are routed through structured metadata and evidence retrieval. Explanations stay separate from authoritative text and disclose missing verification."
          />
          <div className="analysis-box">
            <label
              htmlFor="question"
              className="flex items-center gap-2 text-sm font-medium"
            >
              <Search className="size-4 text-primary" /> Ask about a standard,
              clause, test or BIS service
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="mt-4 min-h-24 w-full resize-none rounded-md border border-input bg-[#0b0c0d] p-3 text-sm leading-6 outline-none focus:border-primary"
            />
            <div className="mt-3 flex justify-between gap-3">
              <p className="text-[11px] text-muted-foreground">
                Language detected: English · Canonical query preserved
              </p>
              <Button
                onClick={ask}
                disabled={answerQuery.isFetching || !question.trim()}
                className="rounded-md"
              >
                {answerQuery.isFetching ? (
                  <LoaderCircle className="animate-spin" />
                ) : (
                  <>
                    Retrieve evidence <ArrowRight />
                  </>
                )}
              </Button>
            </div>
          </div>
          {answerQuery.isPending && <div className="mt-5"><LoadingState label="Retrieving database evidence…" /></div>}
          {answerQuery.isError && <div className="mt-5"><ErrorState message={errorMessage(answerQuery.error)} /></div>}
          {answerQuery.data && (
            <div aria-live="polite" className="mt-5 space-y-5">
              <div className="panel overflow-hidden">
                <div className="panel-header">
                  <div>
                    <span className="eyebrow">Structured answer</span>
                    <h2 className="panel-title">
                      {answerQuery.data.intent.replaceAll('_', ' ')}
                    </h2>
                  </div>
                  <Badge className="bg-amber-300/10 text-amber-300">
                    {Math.round(answerQuery.data.confidence * 100)}% confidence
                  </Badge>
                </div>
                <div className="p-5">
                  <p className="text-sm leading-7 text-foreground/85">
                    {answerQuery.data.answer}
                  </p>
                  <div className="mt-5 grid gap-3 sm:grid-cols-2">
                    {answerQuery.data.warnings.map((item) => (
                      <div
                        key={item}
                        className="flex gap-2 rounded-md border border-border bg-[#0c0d0e] p-3 text-xs"
                      >
                        <CheckCircle2 className="size-3.5 shrink-0 text-cyan-300" />
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="grid gap-5 md:grid-cols-[1.2fr_.8fr]">
                <div className="panel p-5">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <BookOpenText className="size-4 text-primary" /> Evidence
                    used
                  </div>
                  {answerQuery.data.citations.map((citation) => <div key={citation.id} className="mt-4 rounded-md border border-border bg-[#0c0d0e] p-4">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-medium">
                        {citation.document_title}
                      </p>
                      <Badge variant="outline">Demo metadata</Badge>
                    </div>
                    <p className="mt-2 text-xs leading-5 text-muted-foreground">
                      {citation.standard_number ?? citation.document_type} · {citation.version ?? 'version not recorded'}
                    </p>
                    <Button
                      nativeButton={false}
                      render={
                        <Link
                          aria-label="Inspect source record"
                          href={citation.standard_number?.includes('10322') ? '/standards/is-10322-5-8' : '/standards'}
                        />
                      }
                      variant="link"
                      className="mt-2 h-auto p-0 text-xs"
                    >
                      Inspect source record <ArrowRight />
                    </Button>
                  </div>)}
                  {answerQuery.data.citations.length === 0 && <p className="mt-4 text-xs text-muted-foreground">No matching evidence records were found.</p>}
                </div>
                <div className="panel p-5">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <CircleAlert className="size-4 text-amber-300" />{' '}
                    Verification boundary
                  </div>
                  <p className="mt-4 text-xs leading-5 text-muted-foreground">
                    {answerQuery.data.warnings.join(' · ')}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>
    </AppShell>
  );
}
