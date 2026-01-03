/**
 * Shared utilities for generating Artillery performance reports
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Read and embed CSS stylesheet inline in HTML
 */
export function getEmbeddedCSS() {
	const cssSourcePath = path.join(__dirname, ".", "styles", "report-styles.css");

	try {
		if (fs.existsSync(cssSourcePath)) {
			const cssContent = fs.readFileSync(cssSourcePath, "utf8");
			return cssContent;
		}
	} catch (error) {
		console.warn(`⚠️  Could not read CSS file: ${error.message}`);
	}
	return "";
}

/**
 * Get HTML head section with embedded CSS
 */
export function getHTMLHead() {
	const cssContent = getEmbeddedCSS();
	const cssTag = cssContent ? `<style>\n${cssContent}\n</style>` : "";

	return `<!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Artillery Load Test Report</title>
                <script src="https://cdn.tailwindcss.com"></script>
                ${cssTag}
            </head>
            <body class="bg-gray-50">
                <div class="min-h-screen">
        `;
}

/**
 * Generate header section with status and metadata
 */
export function generateHeader(stats, status, statusIcon) {
	return `
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-2xl font-bold text-gray-900">Load Test Report</h1>
          <div class="status-badge ${status === "SUCCEEDED" ? "status-success" : "status-failed"}">
            ${statusIcon} ${status}
          </div>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span class="text-gray-600">Test Suite:</span>
            <p class="font-semibold text-gray-900">${stats.test_suite || "N/A"}</p>
          </div>
          <div>
            <span class="text-gray-600">Environment:</span>
            <p class="font-semibold text-gray-900">${stats.environment || "N/A"}</p>
          </div>
          <div>
            <span class="text-gray-600">App:</span>
            <p class="font-semibold text-gray-900">${stats.app || "N/A"}</p>
          </div>
          <div>
            <span class="text-gray-600">Product:</span>
            <p class="font-semibold text-gray-900">${stats.product || "N/A"}</p>
          </div>
        </div>
      </div>
    </header>`;
}

/**
 * Get HTML footer
 */
export function getHTMLFooter() {
	return `    <!-- Footer -->
                <footer class="bg-white border-t border-gray-200 mt-12 py-6">
                    <div class="max-w-7xl mx-auto px-6 text-center text-sm text-gray-600">
                        <p>Generated on ${new Date().toLocaleString()}</p>
                    </div>
                </footer>
            </div>
        </body>
    </html>`;
}

/**
 * Format bytes to human-readable format
 */
export function formatBytes(bytes) {
	if (bytes === 0) return "0 B";
	const k = 1024;
	const sizes = ["B", "KB", "MB", "GB"];
	const i = Math.floor(Math.log(bytes) / Math.log(k));
	return (bytes / Math.pow(k, i)).toFixed(2) + " " + sizes[i];
}
