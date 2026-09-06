import Link, { type LinkProps } from 'next/link';
import { type ReactNode } from 'react';
import { buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export function ActionLink({ href, children, className, variant = 'default', ariaLabel }: { href: LinkProps['href']; children: ReactNode; className?: string; variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link'; ariaLabel?: string }) {
  return <Link href={href} aria-label={ariaLabel} className={cn(buttonVariants({ variant }), 'min-h-11 rounded-md px-4', className)}>{children}</Link>;
}
