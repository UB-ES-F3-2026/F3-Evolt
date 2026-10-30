import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'
import globals from 'globals'

export default tseslint.config(
  { ignores: ['dist/**', 'coverage/**', 'node_modules/**'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: { parser: tseslint.parser },
      globals: { ...globals.browser },
    },
  },
  { files: ['src/**/*.ts'], languageOptions: { globals: { ...globals.browser } } },
  { files: ['src/**/*.test.ts'], languageOptions: { globals: { ...globals.node } } },
  { files: ['vite.config.ts', 'eslint.config.js'], languageOptions: { globals: { ...globals.node } } },
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
