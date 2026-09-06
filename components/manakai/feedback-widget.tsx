'use client';

import { usePathname } from 'next/navigation';
import { MessageSquareWarning } from 'lucide-react';

export function FeedbackWidget({ context }: { context?: string }) {
  const pathname = usePathname();
  const body = [
    'What was incorrect or confusing?',
    '',
    '<!-- Please do not include personal, confidential, or commercially sensitive information. -->',
    '',
    `Page: ${pathname}`,
    context ? `Context: ${context}` : '',
  ].filter(Boolean).join('\n');
  const href = `https://github.com/aadiandrj-prog/manakai/issues/new?title=${encodeURIComponent('Staging feedback: confusing result')}&body=${encodeURIComponent(body)}`;

  return (
    <a href={href} target="_blank" rel="noreferrer" className="inline-flex min-h-11 items-center gap-2 rounded-md border border-border px-3 text-xs text-muted-foreground transition hover:border-primary/40 hover:text-foreground">
      <MessageSquareWarning className="size-4" /> Report an incorrect or confusing result
    </a>
  );
}
