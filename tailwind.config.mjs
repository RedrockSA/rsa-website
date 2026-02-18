import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1e3a8a',
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        secondary: {
          DEFAULT: '#475569',
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
        accent: {
          DEFAULT: '#3b82f6',
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
      },
      screens: {
        'nav-desktop': '960px',
      },
      fontFamily: {
        sans: ['Raleway', '"Segoe UI"', 'Arial', 'sans-serif'],
        heading: ['Raleway', '"Segoe UI"', 'Arial', 'sans-serif'],
      },
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            '--tw-prose-headings': theme('colors.secondary.700'),
            '--tw-prose-links': theme('colors.accent.DEFAULT'),
            '--tw-prose-body': theme('colors.secondary.800'),
            'a': {
              '&:hover': {
                color: theme('colors.accent.700'),
              },
            },
            'ul': {
              marginTop: '0.25em',
              marginBottom: '0.25em',
            },
            'ol': {
              marginTop: '0.25em',
              marginBottom: '0.25em',
            },
            'li': {
              marginTop: '0',
              marginBottom: '0',
              paddingTop: '0',
              paddingBottom: '0',
            },
            'li p': {
              marginTop: '0',
              marginBottom: '0',
            },
          },
        },
        lg: {
          css: {
            'ul': {
              marginTop: '0.25em',
              marginBottom: '0.25em',
            },
            'ol': {
              marginTop: '0.25em',
              marginBottom: '0.25em',
            },
            'li': {
              marginTop: '0',
              marginBottom: '0',
              paddingTop: '0',
              paddingBottom: '0',
            },
            'li p': {
              marginTop: '0',
              marginBottom: '0',
            },
          },
        },
      }),
    },
  },
  plugins: [typography],
};
