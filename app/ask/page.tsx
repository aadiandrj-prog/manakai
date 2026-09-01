'use client';

import { useState } from 'react';
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

export default function AskPage() {
  const [question, setQuestion] = useState(
    'What tests are relevant to a rechargeable emergency luminaire?',
  );
  const [loading, setLoading] = useState(false);
  const [answered, setAnswered] = useState(true);
  function ask() {
    setLoading(true);
    setAnswered(false);
    window.setTimeout(() => {
      setLoading(false);
      setAnswered(true);
    }, 600);
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
                disabled={loading || !question.trim()}
                className="rounded-md"
              >
                {loading ? (
                  <LoaderCircle className="animate-spin" />
                ) : (
                  <>
                    Retrieve evidence <ArrowRight />
                  </>
                )}
              </Button>
            </div>
          </div>
          {answered && (
            <div aria-live="polite" className="mt-5 space-y-5">
              <div className="panel overflow-hidden">
                <div className="panel-header">
                  <div>
                    <span className="eyebrow">Structured answer</span>
                    <h2 className="panel-title">
                      Testing depends on product classification and the current
                      standard edition
                    </h2>
                  </div>
                  <Badge className="bg-amber-300/10 text-amber-300">
                    Evidence incomplete
                  </Badge>
                </div>
                <div className="p-5">
                  <p className="text-sm leading-7 text-foreground/85">
                    For the seeded emergency-luminaire scenario, the demo
                    testing pathway includes construction and marking review,
                    insulation resistance, electric strength, endurance and
                    emergency-mode photometry. These are workflow fixtures, not
                    quoted requirements.
                  </p>
                  <div className="mt-5 grid gap-3 sm:grid-cols-2">
                    {[
                      'Insulation resistance and electric strength',
                      'Emergency-mode endurance and photometry',
                      'Construction and marking review',
                      'Battery/charging behaviour',
                    ].map((item) => (
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
                  <div className="mt-4 rounded-md border border-border bg-[#0c0d0e] p-4">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-medium">
                        IS 10322 (Part 5/Sec 8):2013
                      </p>
                      <Badge variant="outline">Demo metadata</Badge>
                    </div>
                    <p className="mt-2 text-xs leading-5 text-muted-foreground">
                      Scope record and seeded product-to-test mapping. No clause
                      text was retrieved.
                    </p>
                    <Button
                      nativeButton={false}
                      render={
                        <Link
                          aria-label="Inspect source record"
                          href="/standards/is-10322-5-8"
                        />
                      }
                      variant="link"
                      className="mt-2 h-auto p-0 text-xs"
                    >
                      Inspect source record <ArrowRight />
                    </Button>
                  </div>
                </div>
                <div className="panel p-5">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <CircleAlert className="size-4 text-amber-300" />{' '}
                    Verification boundary
                  </div>
                  <p className="mt-4 text-xs leading-5 text-muted-foreground">
                    I could not verify exact clause numbers or current
                    requirements from the available authorised BIS sources.
                    Connect the document source before using this as a test
                    plan.
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
