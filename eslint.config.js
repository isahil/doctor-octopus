export default [
  {
    name: "doctor-octopus-eslint",
    files: ["**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx"],
    ignores: ["**/node_modules/", "**/test_reports/**/*", "**/dist/**/*", "**/build/**/*"],
    languageOptions: {
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    rules: {
      "no-unused-vars": "warn",
      quotes: ["warn", "double"],
      "no-trailing-spaces": "error",
      "eol-last": ["error", "always"],
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },
]
