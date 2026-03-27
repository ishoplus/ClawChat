import globals from 'globals'
import pluginVue from 'eslint-plugin-vue'
import vueParser from 'vue-eslint-parser'
import tseslint from 'typescript-eslint'

const tsConfig = tseslint.configs.recommended

export default [
  // Ignore patterns
  {
    ignores: ['**/dist/**', '**/node_modules/**', '**/coverage/**', 'public/**']
  },
  
  // Vue plugin config - essential for Vue 3
  ...pluginVue.configs['flat/essential'],
  
  // Browser globals
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2021
      }
    }
  },
  
  // Vue files with TypeScript
  {
    files: ['**/*.vue'],
    plugins: {
      vue: pluginVue
    },
    processor: pluginVue.processors['.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tseslint.parser,
        ecmaVersion: 2022,
        sourceType: 'module'
      }
    },
    rules: {
      // Relax some rules for this project
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'off',
      'vue/require-default-prop': 'off',
      'vue/require-explicit-emits': 'off',
      'no-console': 'off',
      'no-debugger': 'off',
      'no-empty': 'warn',
      'no-unused-vars': 'off'
    }
  },
  
  // TypeScript files
  {
    files: ['**/*.ts', '**/*.tsx'],
    ...(Array.isArray(tsConfig) ? tsConfig[0] : tsConfig),
    rules: {
      'no-unused-vars': ['warn', { 
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_'
      }],
      '@typescript-eslint/no-explicit-any': 'warn',
      'no-empty': 'warn'
    }
  }
]
