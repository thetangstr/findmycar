/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: process.env.NODE_ENV === 'production' ? 'export' : undefined, // Static site generation only for production
  distDir: 'out',
  images: {
    unoptimized: true,
    domains: [
      'images.unsplash.com', 
      'via.placeholder.com', 
      'cdn.bringatrailer.com',
      'cdn-dealereprocess.com',
      'static.cargurus.com',
      'media.ed.edmunds-media.com',
      'inv.assets.sincrod.com',
      'media-service.carmax.com',
      'platform.cstatic-images.com',
      'images.dealer.com',
      'img2.carmax.com',
      'img.vast.com',
      'content.homenetiol.com',
      'carfax-img.vast.com',
      'pictures.dealer.com',
      'di-uploads-development.dealerinspire.com',
      'dmi.images.fisheye.tv',
      'i.ebayimg.com',
      'img.autobytel.com',
      'auto.dev'
    ],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
};

module.exports = nextConfig;
