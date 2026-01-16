import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'RiskAdvisor v4.0 | Enterprise Decision Intelligence',
    description: 'Transform aviation safety analytics into autonomous decisions',
    keywords: ['aviation', 'safety', 'risk management', 'decision intelligence', 'AI'],
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <body className="min-h-screen bg-dark-950">
                {children}
            </body>
        </html>
    );
}
