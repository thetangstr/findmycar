import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import Layout from '@/components/Layout';
import Head from 'next/head';
import { AuthProvider } from '@/utils/auth';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>FindMyCar - Find Your Perfect Vehicle</title>
        <meta name="description" content="FindMyCar helps you find, compare, and save your favorite vehicles." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <AuthProvider>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </AuthProvider>
    </>
  );
}
