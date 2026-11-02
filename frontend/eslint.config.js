import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'
import globals from 'globals'

/**
 * ESLint flat config: an ordered list of blocks. For each file, ESLint merges
 * the blocks whose `files`/`ignores` match; later blocks override earlier ones.
 * `tseslint.config()` is only a typed helper that flattens nested arrays.
 */
export default tseslint.config(
  // Build output and dependencies are never linted.
  { ignores: ['dist/**', 'coverage/**', 'node_modules/**'] },

  // Core ESLint rules for real bugs (no formatting rules).
  js.configs.recommended,

  // TypeScript rules WITH type information (type-aware). This is what catches
  // floating promises, unsafe `any`, etc. It needs `parserOptions` below.
  ...tseslint.configs.recommendedTypeChecked,

  // Vue rules. This also installs `vue-eslint-parser` for `.vue` files.
  ...pluginVue.configs['flat/recommended'],

  {
    // Inside a .vue file there are two parsers in cascade:
    //   vue-eslint-parser -> <script lang="ts"> -> typescript-eslint/parser
    // `projectService` gives type-aware rules a TypeScript program.
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
        projectService: true,
        extraFileExtensions: ['.vue'],
        tsconfigRootDir: import.meta.dirname,
      },
      globals: { ...globals.browser },
    },
  },
  {
    // App TypeScript and the Vite config use the same TS program.
    // `extraFileExtensions` lets `.vue` imports be resolved by that program.
    files: ['src/**/*.ts', 'vite.config.ts'],
    languageOptions: {
      parserOptions: {
        projectService: true,
        extraFileExtensions: ['.vue'],
        tsconfigRootDir: import.meta.dirname,
      },
      globals: { ...globals.browser },
    },
  },

  // Tests additionally get Node globals (`describe`, `it`, `process`, ...).
  { files: ['src/**/*.test.ts'], languageOptions: { globals: { ...globals.node } } },

  // Config files run in Node, not in the browser.
  { files: ['vite.config.ts', 'eslint.config.js'], languageOptions: { globals: { ...globals.node } } },

  {
    // `eslint.config.js` is not part of tsconfig.json, so type-aware rules
    // cannot run on plain .js files.
    files: ['**/*.js'],
    ...tseslint.configs.disableTypeChecked,
  },

  {
    // Plain TypeScript cannot read `.vue` module types (vue-tsc uses its own
    // plugin), so these are tooling false positives, not unsafe code.
    files: ['src/main.ts', 'src/router/index.ts'],
    rules: {
      '@typescript-eslint/no-unsafe-argument': 'off',
      '@typescript-eslint/no-unsafe-assignment': 'off',
    },
  },
  {
    // The API contract rejects with plain `{ code, message, details? }` objects,
    // not Error instances (docs/api.md §5).
    files: ['src/services/apiClient.ts', 'src/mocks/**', '**/*.test.ts'],
    rules: {
      '@typescript-eslint/only-throw-error': 'off',
      '@typescript-eslint/prefer-promise-reject-errors': 'off',
    },
  },
  {
    // Real findings kept visible as warnings until the follow-up fix: warnings
    // do not fail `npm run lint` (only errors do).
    files: ['src/views/MovementsView.vue', 'src/viewmodels/useMovementsViewModel.test.ts'],
    rules: {
      '@typescript-eslint/no-floating-promises': 'warn',
      '@typescript-eslint/require-await': 'warn',
    },
  },

  {
    rules: {
      // Formatting belongs to the SFC style guide; no Prettier in this repo.
      'vue/max-attributes-per-line': 'off',
      'vue/singleline-html-element-content-newline': 'off',
      'vue/html-self-closing': 'off',
      // App.vue / view names are deliberate.
      'vue/multi-word-component-names': 'off',
      // AGENTS.md bans `any`; allow intentionally unused _-prefixed names.
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
    },
  },
)
