import type { Metadata } from 'next';
import './globals.css';
import { Providers } from './providers';

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000',
  ),
  title: 'ManakAI — Indian Standards & BIS Compliance Intelligence',
  description:
    'Evidence-first product compliance, standards discovery, testing guidance and BIS service navigation.',
  openGraph: {
    title: 'ManakAI',
    description: 'Indian Standards & BIS Compliance Intelligence',
    type: 'website',
    images: [
      {
        url: '/og.png',
        width: 1731,
        height: 909,
        alt: 'ManakAI — Indian Standards & BIS Compliance Intelligence',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ManakAI',
    description: 'Indian Standards & BIS Compliance Intelligence',
    images: ['/og.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased"><Providers>{children}</Providers></body>
    </html>
  );
}
