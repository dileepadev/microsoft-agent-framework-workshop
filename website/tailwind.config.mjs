import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        surface: {
          DEFAULT: '#ffffff',
          dark: '#0f1117',
        },
        border: {
          DEFAULT: '#e5e7eb',
          dark: '#1e1e2e',
        },
        muted: {
          DEFAULT: '#f9fafb',
          dark: '#1a1a26',
        },
      },
      backgroundColor: {
        'page':      '#ffffff',
        'page-dark': '#0c0c11',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', '"Cascadia Code"', 'monospace'],
      },
      animation: {
        'fade-up':    'fadeUp 0.5s ease-out both',
        'fade-in':    'fadeIn 0.4s ease-out both',
        'float':      'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 8s ease-in-out infinite',
      },
      keyframes: {
        fadeUp: {
          '0%':   { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':       { transform: 'translateY(-12px)' },
        },
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: theme('colors.gray[700]'),
            '--tw-prose-headings': theme('colors.gray[900]'),
            '--tw-prose-links':    theme('colors.primary[600]'),
            '--tw-prose-code':     theme('colors.primary[700]'),
            '--tw-prose-bold':     theme('colors.gray[900]'),
            '--tw-prose-counters': theme('colors.primary[500]'),
            '--tw-prose-bullets':  theme('colors.primary[400]'),
            'h1, h2, h3, h4': {
              'scroll-margin-top': '5rem',
              'font-weight': '700',
            },
            a: {
              'font-weight': '500',
              'text-decoration': 'underline',
              'text-underline-offset': '3px',
              'text-decoration-color': theme('colors.primary[300]'),
              '&:hover': {
                'text-decoration-color': theme('colors.primary[500]'),
              },
            },
            code: {
              'font-family': '"JetBrains Mono", monospace',
              'font-size': '0.875em',
              'font-weight': '500',
              'background': theme('colors.primary[50]'),
              'padding': '0.2em 0.4em',
              'border-radius': '0.3em',
              'border': `1px solid ${theme('colors.primary[100]')}`,
            },
            'code::before': { content: '""' },
            'code::after':  { content: '""' },
            pre: {
              'border-radius': '0.75rem',
              'border': `1px solid ${theme('colors.gray[200]')}`,
            },
            'pre code': {
              'background': 'transparent',
              'padding': '0',
              'border': 'none',
              'font-size': '0.875em',
            },
          },
        },
        invert: {
          css: {
            color: theme('colors.gray[300]'),
            '--tw-prose-headings': theme('colors.white'),
            '--tw-prose-links':    theme('colors.primary[400]'),
            '--tw-prose-code':     theme('colors.primary[300]'),
            '--tw-prose-bold':     theme('colors.white'),
            '--tw-prose-counters': theme('colors.primary[400]'),
            '--tw-prose-bullets':  theme('colors.primary[500]'),
            code: {
              'background': 'rgba(99,102,241,0.12)',
              'border-color': 'rgba(99,102,241,0.2)',
              'color': theme('colors.primary[300]'),
            },
            pre: {
              'border-color': 'rgba(255,255,255,0.06)',
            },
          },
        },
      }),
    },
  },
  plugins: [typography],
};
