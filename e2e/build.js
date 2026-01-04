import esbuild from "esbuild";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const buildOptions = {
	entryPoints: [
		"./client/**/*.js",
		"./perf/*.js",
		// Add any other entry points that need to be bundled
	],
	outdir: "dist",
	format: "cjs", // CommonJS output
	platform: "node",
	external: ["playwright"], // Don't bundle heavy dependencies
	bundle: true,
	minify: false, // Set to true for production
};

esbuild
	.build(buildOptions)
	.then(() => {
		// Create dist/package.json to declare CommonJS module type
		const distPackageJson = path.join(__dirname, "dist", "package.json");
		fs.mkdirSync(path.join(__dirname, "dist"), { recursive: true });
		fs.writeFileSync(distPackageJson, JSON.stringify({ type: "commonjs" }, null, 2));
		console.log("✅ Build complete: dist/");
	})
	.catch(() => process.exit(1));
