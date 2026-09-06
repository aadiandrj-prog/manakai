'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { CircleAlert, LoaderCircle, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function LoadingState({ label = 'Loading database records…' }: { label?: string }) {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    const timer = window.setTimeout(() => setSlow(true), 3500);
    return () => window.clearTimeout(timer);
  }, []);
  return (
    <div aria-live="polite" aria-busy="true" className="panel grid min-h-56 place-items-center px-5 text-center">
      <div><LoaderCircle className="mx-auto size-6 animate-spin text-primary" /><p className="mt-3 text-sm">{label}</p>{slow && <p className="mt-2 max-w-md text-xs leading-5 text-muted-foreground">Connecting to the ManakAI regulatory service. Free staging may take up to a minute to wake up; your previous verified data is not being changed.</p>}</div>
    </div>
  );
}

export function ErrorState({ message, onRetry, actionHref, actionLabel = 'Check a product' }: { message: string; onRetry?: () => void; actionHref?: string; actionLabel?: string }) {
  return (
    <div role="alert" className="panel flex min-h-40 items-start gap-3 p-5 text-sm text-amber-100">
      <CircleAlert className="size-5 shrink-0 text-amber-300" />
      <div><p className="font-medium">We couldn’t load this information</p><p className="mt-1 max-w-xl text-xs leading-5 text-muted-foreground">{message}</p><div className="mt-4 flex flex-wrap gap-2">{onRetry && <Button size="sm" variant="outline" onClick={onRetry}><RotateCcw /> Try again</Button>}{actionHref && <Button size="sm" nativeButton={false} render={<Link href={actionHref} />}>{actionLabel}</Button>}</div></div>
    </div>
  );
}
