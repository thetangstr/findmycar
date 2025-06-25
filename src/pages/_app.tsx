import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import Layout from '@/components/Layout';
import Head from 'next/head';
import { useEffect } from 'react';
import { AuthProvider } from '@/utils/auth';
import { cleanupGarbledElements } from '@/utils/cleanupUtils';
import ErrorBoundary from '@/components/ErrorBoundary';
import { ToastProvider } from '@/contexts/ToastContext';

export default function App({ Component, pageProps }: AppProps) {
  // Run cleanup utility when component mounts (client-side only)
  useEffect(() => {
    // Clean up any garbled text elements that might be injected
    cleanupGarbledElements();
  }, []);

  return (
    <>
      <Head>
        <title>FindMyCar - Find Your Perfect Vehicle</title>
        <meta name="description" content="FindMyCar helps you find, compare, and save your favorite vehicles." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="stylesheet" href="/cleanup.css" />
      </Head>
      <ErrorBoundary>
        <ToastProvider>
          <AuthProvider>
            <Layout>
              <Component {...pageProps} />
            </Layout>
          </AuthProvider>
        </ToastProvider>
      </ErrorBoundary>
    </>
  );
}
