module.exports = {
    root: true,
    env: { browser: true, es2020: true },
    extends: [
        'eslint:recommended',
        'plugin:@typescript-eslint/recommended',
        'plugin:react-hooks/recommended',
    ],
    ignorePatterns: ['dist', '.eslintrc.cjs'],
    parser: '@typescript-eslint/parser',
    plugins: ['react-refresh'],
    rules: {
        'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
        '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    },
    overrides: [
        {
            // Exporting a hook next to its provider is the idiomatic React
            // context pattern. Splitting six files to satisfy an HMR lint rule
            // costs more than the fast-refresh edge case it protects.
            files: ['src/contexts/*.tsx'],
            rules: { 'react-refresh/only-export-components': 'off' },
        },
    ],
}
