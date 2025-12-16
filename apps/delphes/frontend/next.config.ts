import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone', // Nécessaire pour Docker
  turbopack: {
    // Définir explicitement le répertoire racine pour Turbopack
    root: __dirname,
  },
  // Supprimer la configuration webpack quand on utilise Turbopack
  ...(process.env.NODE_ENV === 'development' ? {} : {
    webpack: (config) => {
      // Support des fonts .woff2 (seulement en production)
      config.module.rules.push({
        test: /\.woff2$/,
        type: "asset/resource",
      });
      return config;
    },
  }),
};

export default nextConfig;
