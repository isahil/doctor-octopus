export default [
    {
        name: "doctor-ocotopus-eslint",
        files: ["**/*.js", "**/*.ts"],
        ignores: ["**/node_modules/", "**/test_reports/**/*", "**/dist/**/*", "**/build/**/*"],
        rules: {
            "no-unused-vars": "warn"
        }
    }
];