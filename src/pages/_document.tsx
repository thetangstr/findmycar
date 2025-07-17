import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head />
      <body>
        <Main />
        <NextScript />
        {/* Toast portal container */}
        <div id="toast-root" />
      </body>
    </Html>
  );
}