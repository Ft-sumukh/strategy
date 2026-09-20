import type { Metadata } from 'next';
import './globals.css';
import { AppShell } from '../components/layout/AppShell';

export const metadata: Metadata = {
  title: 'AEGIS INVEST — AI Decision-Intelligence Platform',
  description:
    'AI-assisted, risk-aware financial decision-intelligence platform combining quantitative strategies, risk modeling, and transparent analysis.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#070A11] text-slate-100 min-h-screen antialiased selection:bg-blue-600/30 selection:text-white">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
