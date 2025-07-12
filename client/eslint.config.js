export default [
  {
    name: "doctor-octopus-eslint",
    files: ["**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx", "**/*.json"],
    ignores: ["**/node_modules/", "**/test_reports/**/*", "**/dist/**/*", "**/build/**/*"],
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
