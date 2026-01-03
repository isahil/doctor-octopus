import fs from "fs";
import path from "path";
import { 
	getHTMLHead,
	getHTMLFooter,
	generateHeader ,
	generateSummaryMetrics,
	generateHTTPStatusCodes,
	generateErrorsSection,
	generateResponseTimePercentiles,
	generateIntermediateResults,
} from "./index.js";
import { ensure_dir } from "../../client/utils/fs_helper.js";

/**
 * Main entry point: Generate complete HTML report by composing sections
 */
function generateHTML(data, outputPath, outputDir) {
	const { aggregate, intermediate, stats } = data;

	// Determine status
	const failedVusers = aggregate.counters["vusers.failed"] || 0;
	const status = failedVusers > 0 ? "FAILED" : "SUCCEEDED";
	const statusIcon = status === "SUCCEEDED" ? "✅" : "❌";

	// HTTP metrics
	const httpResponses = aggregate.counters["http.responses"] || 0;
	const httpDownloadedBytes = aggregate.counters["http.downloaded_bytes"] || 0;
	const requestRate = aggregate.rates["http.request_rate"] || 0;

	// Response time summaries
	const responseTimeSummary = aggregate.summaries["http.response_time"] || {};

	// Ensure output directory exists
	ensure_dir(outputDir);

	// Get HTML head with embedded CSS
	const html = getHTMLHead();

	// Compose all sections
	const sections = `
    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-6 py-8">
${generateHeader(stats, status, statusIcon)}
${generateSummaryMetrics(aggregate, responseTimeSummary, httpDownloadedBytes, httpResponses, requestRate)}
${generateHTTPStatusCodes(aggregate, httpResponses)}
${generateErrorsSection(aggregate)}
${generateResponseTimePercentiles(responseTimeSummary)}
${generateIntermediateResults(intermediate)}
    </main>
${getHTMLFooter()}`;
	fs.writeFileSync(outputPath, html + sections);
	console.log(`✅ Report generated: ${outputPath}`);
}

/**
 * Entry point: Parse arguments and generate report
 */
const args = process.argv.slice(2);
if (args.length < 2) {
	console.error("❌ Usage: node haiku_perf_report.js <input.json> <output-directory>");
	process.exit(1);
}

const inputPath = args[0];
const outputDir = args[1];

try {
	// Generate filename - always create index.html
	const outputFilename = path.join(outputDir, "index.html");

	// Read and parse JSON
	const data = JSON.parse(fs.readFileSync(inputPath, "utf8"));
	generateHTML(data, outputFilename, outputDir);
	console.log(
		`📊 Report data: ${data.aggregate.counters["vusers.created"]} VUsers, ${data.aggregate.counters["http.requests"]} Requests`
	);
} catch (error) {
	console.error("❌ Error:", error.message);
	process.exit(1);
}
