import { CircleAlert, LoaderCircle } from 'lucide-react';

export function LoadingState({ label = 'Loading database records…' }: { label?: string }) {
  return (
    <div aria-live="polite" className="panel grid min-h-56 place-items-center text-center">
      <div><LoaderCircle className="mx-auto size-6 animate-spin text-primary" /><p className="mt-3 text-sm">{label}</p></div>
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div role="alert" className="panel flex min-h-40 items-center gap-3 p-5 text-sm text-amber-100">
      <CircleAlert className="size-5 shrink-0 text-amber-300" />
      <div><p className="font-medium">Data could not be loaded</p><p className="mt-1 text-xs text-muted-foreground">{message}</p></div>
    </div>
  );
}
