import fs from "fs";
import path from "path";
import {
	get_HTML_head,
	get_HTML_footer,
	generate_header,
	generate_summary_metrics,
	generate_HTTP_status_codes,
	generate_errors_section,
	generate_response_time_percentiles,
	generate_intermediate_results,
	generate_web_vitals,
	generate_browser_metrics,
	generate_vu_session_length_stats,
	generate_test_scenario,
	generate_screenshots_section,
	html_utils,
} from "./index.js";
import { ensure_dir } from "../../client/utils/fs_helper.js";

/**
 * Main entry point: Generate complete HTML report by composing sections
 */
function generate_HTML(data, outputPath, outputDir) {
	const { aggregate, intermediate, stats } = data;

	// Determine status
	const failed_vusers = aggregate.counters["vusers.failed"] || 0;
	const status = failed_vusers > 0 ? "UNSTABLE" : "STABLE";
	const status_icon = status === "STABLE" ? "✅" : "⚠️";

	// HTTP metrics
	const httpResponses = aggregate.counters["http.responses"] || 0;
	const httpDownloadedBytes = aggregate.counters["http.downloaded_bytes"] || 0;
	const requestRate = aggregate.rates["http.request_rate"] || 0;
	const responseTimeSummary = aggregate.summaries["http.response_time"] || {};

	// Get screenshots if they exist
	const screenshots_dir = path.join(outputDir, "screenshots");
	let screenshots = [];
	if (fs.existsSync(screenshots_dir)) {
		const files = fs.readdirSync(screenshots_dir);
		screenshots = files
			.filter((file) => /\.(png|jpg|jpeg|gif)$/i.test(file))
			.map((file) => `screenshots/${file}`);
	}

	// Ensure output directory exists
	ensure_dir(outputDir);

	// Get HTML head with embedded CSS
	const html = get_HTML_head();

	// Compose all sections
	const sections = `
    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-6 py-8">
${generate_header(stats, status, status_icon)}
${generate_summary_metrics(aggregate, responseTimeSummary, httpDownloadedBytes, httpResponses, requestRate)}
${generate_test_scenario(aggregate.summaries)}
${generate_vu_session_length_stats(aggregate.summaries)}
${generate_HTTP_status_codes(aggregate, httpResponses)}
${generate_errors_section(aggregate)}
${generate_response_time_percentiles(responseTimeSummary)}
${generate_web_vitals(aggregate.summaries)}
${generate_browser_metrics(aggregate)}
${generate_intermediate_results(intermediate)}
${generate_screenshots_section(screenshots)}
    </main>
${get_HTML_footer()}
${html_utils()}
    `;
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

const input_path = args[0];
const output_dir = args[1];

try {
	// Generate filename - always create index.html
	const output_filename = path.join(output_dir, "index.html");
	const data = JSON.parse(fs.readFileSync(input_path, "utf8"));
	generate_HTML(data, output_filename, output_dir);
	console.log(
		`📊 Report data: created - ${data.aggregate.counters["vusers.created"]} VUsers, failed - ${data.aggregate.counters["vusers.failed"]}`,
	);
} catch (error) {
	console.error("❌ Error:", error.message);
	process.exit(1);
}
