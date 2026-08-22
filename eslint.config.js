import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  {
    ignores: [
      'dist',
      'playwright-report',
      'playwright-performance-report',
      'test-results',
      'node_modules',
      '.local',
      '.cache',
      '.agents',
      'artifacts',
      '.pythonlibs',
      '.venv',
    ],
  },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      // JSX-only component arguments (for example `icon: Icon`) are not
      // counted as reads by ESLint's core rule without the React plugin.
      'no-unused-vars': ['error', {
        varsIgnorePattern: '^[A-Z_]',
        argsIgnorePattern: '^[A-Z_]',
      }],
      // The project intentionally co-locates shadcn variants and context hooks
      // with their components; these exports are stable and do not affect runtime refresh.
      'react-refresh/only-export-components': 'off',
    },
  },
]
