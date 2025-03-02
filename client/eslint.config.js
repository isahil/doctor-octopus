export default [
  {
    name: "doctor-ocotopus-eslint",
    files: ["**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx"],
    ignores: ["**/node_modules/", "**/test_reports/**/*", "**/dist/**/*", "**/build/**/*"],
    rules: {
      "no-unused-vars": "warn",
      quotes: ["warn", "double"],
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },
]
