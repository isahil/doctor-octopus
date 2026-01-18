import { format_bytes, generate_info_icon } from "./index.js";
import explanations from "./explanations.json" with { type: "json" };

/**
 * Generate summary metrics section (includes test timing)
 */
export function generate_summary_metrics(
	aggregate,
	response_time_summary,
	http_downloaded_bytes,
	http_responses,
	request_rate,
) {
	const total_vusers = aggregate.counters["vusers.created"] || 0;
	const completed_vusers = aggregate.counters["vusers.completed"] || 0;
	const failed_vusers = aggregate.counters["vusers.failed"] || 0;
	const http_requests = aggregate.counters["http.requests"] || 0;

	// Extract custom counters (exclude standard Artillery counters)
	const standard_counter_prefixes = ["vusers.", "http.", "browser.", "errors.", "plugins."];
	const custom_counters = Object.entries(aggregate.counters)
		.filter(([key]) => {
			const is_standard = standard_counter_prefixes.some((prefix) => key.startsWith(prefix));
			return !is_standard;
		})
		.map(([key, value]) => ({
			name: key.replace(/_/g, " "),
			value: value,
		}));

	const custom_metrics_HTML =
		custom_counters.length > 0
			? `
		<div class="mt-4 pt-4 border-t border-gray-600">
			<div class="text-sm font-semibold text-gray-300 mb-3">Custom Metrics</div>
			<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
				${custom_counters
					.map(
						({ name, value }) => `
				<div class="custom-metric-item">
					<div class="text-xs text-gray-400">${name}</div>
					<div class="text-lg font-semibold text-blue-400">${value.toLocaleString()}</div>
				</div>
				`,
					)
					.join("")}
			</div>
		</div>`
			: "";

	// Extract test timing information
	const start_time = aggregate.firstCounterAt
		? new Date(aggregate.firstCounterAt).toLocaleString()
		: "N/A";
	const end_time = aggregate.lastCounterAt
		? new Date(aggregate.lastCounterAt).toLocaleString()
		: "N/A";
	const duration =
		aggregate.firstCounterAt && aggregate.lastCounterAt
			? ((aggregate.lastCounterAt - aggregate.firstCounterAt) / 1000).toFixed(2)
			: "N/A";

	return `
    <!-- Summary Metrics -->
    <section class="mb-8">
    <div class="section-title-container">
      <h2 class="text-xl font-semibold text-gray-100 mb-4">Summary Metrics</h2>
      ${generate_info_icon(explanations.summary_metrics.description)}
    </div>
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- Virtual Users -->
      ${
			total_vusers > 0
				? `
      <div class="metric-card">
      <div class="metric-label">Virtual Users Created</div>
      <div class="metric-value">${total_vusers.toLocaleString()}</div>
      <div class="text-xs text-gray-400 mt-2">
        <span class="success-indicator font-semibold">${completed_vusers}</span> completed, 
        <span class="failed-indicator font-semibold">${failed_vusers}</span> failed
      </div>
      </div>
      `
				: ""
		}

      <!-- HTTP Requests -->
      ${
			http_requests > 0
				? `
      <div class="metric-card">
      <div class="metric-label">HTTP Requests</div>
      <div class="metric-value">${http_requests.toLocaleString()}</div>
      <div class="text-xs text-gray-400 mt-2">${request_rate.toFixed(2)} req/s average</div>
      </div>
      `
				: ""
		}

      <!-- Response Time -->
      ${
			response_time_summary?.mean
				? `
      <div class="metric-card">
      <div class="metric-label">Avg Response Time</div>
      <div class="metric-value">${response_time_summary.mean.toFixed(1)}<span class="text-sm">ms</span></div>
      <div class="text-xs text-gray-400 mt-2">p95: ${(response_time_summary.p95 || 0).toFixed(1)}ms</div>
      </div>
      `
				: ""
		}

      <!-- Downloaded Data -->
      ${
			http_downloaded_bytes > 0
				? `
      <div class="metric-card">
      <div class="metric-label">Data Downloaded</div>
      <div class="metric-value text-lg">${format_bytes(http_downloaded_bytes)}</div>
      <div class="text-xs text-gray-400 mt-2">${http_responses} responses</div>
      </div>
      `
				: ""
		}

      <!-- Test Start Time -->
      <div class="metric-card">
      <div class="metric-label">Test Start</div>
      <div class="text-sm text-gray-100 font-semibold">${start_time}</div>
      </div>

      <!-- Test End Time -->
      <div class="metric-card">
      <div class="metric-label">Test End</div>
      <div class="text-sm text-gray-100 font-semibold">${end_time}</div>
      </div>

      <!-- Total Duration -->
      <div class="metric-card">
      <div class="metric-label">Total Duration</div>
      <div class="metric-value text-lg">${duration}s</div>
      </div>
    </div>
    ${custom_metrics_HTML}
    </section>`;
}

/**
 * Generate HTTP status codes section
 */
export function generate_HTTP_status_codes(aggregate, http_responses) {
	if (http_responses === 0) {
		return "";
	}
	const status_codes = Object.keys(aggregate.counters)
		.filter((key) => key.startsWith("http.codes."))
		.map((key) => ({
			code: key.replace("http.codes.", ""),
			count: aggregate.counters[key],
		}));

	return `
      <!-- HTTP Status Codes -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">HTTP Status Codes</h2>
          ${generate_info_icon(explanations.http_status_codes.description)}
        </div>
        <div class="section-container">
          <table>
            <thead>
              <tr>
                <th>Status Code</th>
                <th>Count</th>
                <th>Percentage</th>
              </tr>
            </thead>
            <tbody>
              ${status_codes
					.map(({ code, count }) => {
						const percentage = ((count / http_responses) * 100).toFixed(1);
						const isSuccess = code.startsWith("2");
						return `<tr>
                  <td>
                    <span class="status-code-badge ${isSuccess ? "status-code-success" : "status-code-error"}">
                      ${code}
                    </span>
                  </td>
                  <td class="font-semibold">${count.toLocaleString()}</td>
                  <td>${percentage}%</td>
                </tr>`;
					})
					.join("")}
            </tbody>
          </table>
        </div>
      </section>`;
}

/**
 * Generate errors section (only if errors exist)
 */
export function generate_errors_section(aggregate) {
	const errors = {};
	Object.keys(aggregate.counters).forEach((key) => {
		if (key.startsWith("errors.")) {
			const errorType = key.replace("errors.", "");
			errors[errorType] = aggregate.counters[key];
		} else if (key.includes(".errors.")) {
			const match = key.match(/\.errors\.(\w+)/);
			if (match) {
				errors[match[1]] = (errors[match[1]] || 0) + aggregate.counters[key];
			}
		}
	});

	if (Object.keys(errors).length === 0) {
		return "";
	}

	return `
      <!-- Errors Section -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">Errors</h2>
          ${generate_info_icon(explanations.errors.description)}
        </div>
        <div class="section-container">
          <table>
            <thead>
              <tr>
                <th>Error Type</th>
                <th>Count</th>
              </tr>
            </thead>
            <tbody>
              ${Object.entries(errors)
					.map(
						([type, count]) => `
              <tr>
                <td class="font-medium">${type}</td>
                <td class="font-semibold failed-indicator">${count.toLocaleString()}</td>
              </tr>
              `,
					)
					.join("")}
            </tbody>
          </table>
        </div>
      </section>`;
}

/**
 * Generate response time percentiles section
 */
export function generate_response_time_percentiles(response_time_summary) {
	if (!response_time_summary || Object.keys(response_time_summary).length === 0) {
		return "";
	}
	return `
      <!-- Response Time Percentiles -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">Response Time Percentiles</h2>
          ${generate_info_icon(explanations.response_time_percentiles.description)}
        </div>
        <div class="section-container">
          <div class="percentiles-grid">
            <div class="percentile-item">
              <div class="label">Min</div>
              <div class="value">${(response_time_summary.min || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p50 (Median)</div>
              <div class="value">${(response_time_summary.p50 || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p75</div>
              <div class="value">${(response_time_summary.p75 || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p90</div>
              <div class="value">${(response_time_summary.p90 || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p95</div>
              <div class="value">${(response_time_summary.p95 || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p99</div>
              <div class="value">${(response_time_summary.p99 || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">Max</div>
              <div class="value">${(response_time_summary.max || 0).toFixed(1)}ms</div>
            </div>
          </div>
        </div>
      </section>`;
}

/**
 * Generate session length statistics section
 */
export function generate_vu_session_length_stats(summaries) {
	const session_length_data = summaries?.["vusers.session_length"];

	if (!session_length_data) {
		return ""; // Skip if there's no session length data
	}

	return `
      <!-- VU Session Statistics -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">VU Session Statistics</h2>
          ${generate_info_icon(explanations.vu_session_length_stats.description)}
        </div>
        <div class="section-container">
          <div class="percentiles-grid">
            <div class="percentile-item">
              <div class="label">Min Duration</div>
              <div class="value">${session_length_data.min ? session_length_data.min.toFixed(0) : "N/A"}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p50 (Median)</div>
              <div class="value">${session_length_data.p50 ? session_length_data.p50.toFixed(0) : "N/A"}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">Mean Duration</div>
              <div class="value">${session_length_data.mean ? session_length_data.mean.toFixed(0) : "N/A"}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p95</div>
              <div class="value">${session_length_data.p95 ? session_length_data.p95.toFixed(0) : "N/A"}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p99</div>
              <div class="value">${session_length_data.p99 ? session_length_data.p99.toFixed(0) : "N/A"}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">Max Duration</div>
              <div class="value">${session_length_data.max ? session_length_data.max.toFixed(0) : "N/A"}ms</div>
            </div>
          </div>
        </div>
      </section>`;
}

/**
 * Generate trace collection stats
 */
export function generate_trace_stats(aggregate) {
	const traces_collected = aggregate.counters["browser.traces_collected"] || 0;
	const traces_discarded = aggregate.counters["browser.traces_discarded"] || 0;
	const total_traces = traces_collected + traces_discarded;
	const collection_rate =
		total_traces > 0 ? ((traces_collected / total_traces) * 100).toFixed(1) : 0;

	if (total_traces === 0) {
		return ""; // Skip if no traces collected
	}

	return `
      <!-- Trace Collection Stats -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">Trace Collection</h2>
          ${generate_info_icon(explanations.trace_stats.description)}
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="metric-card">
            <div class="metric-label">Traces Collected</div>
            <div class="metric-value success-indicator">${traces_collected.toLocaleString()}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Traces Discarded</div>
            <div class="metric-value failed-indicator">${traces_discarded.toLocaleString()}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Total Traces</div>
            <div class="metric-value">${total_traces.toLocaleString()}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Collection Rate</div>
            <div class="metric-value success-indicator">${collection_rate}%</div>
          </div>
        </div>
      </section>`;
}

/**
 * Generate intermediate results section
 */
export function generate_intermediate_results(intermediate) {
	const intermediate_rows = intermediate
		.map((period) => {
			const timestamp = new Date(parseInt(period.period)).toLocaleString();
			const vusers = period.counters["vusers.created"] || 0;
			const requests = period.counters["http.requests"] || 0;
			const rate = period.rates["http.request_rate"] || 0;
			const p95 = period.summaries?.["http.response_time"]?.p95 || "N/A";
			const period_errors = Object.keys(period.counters)
				.filter((key) => key.includes("errors"))
				.reduce((sum, key) => sum + (period.counters[key] || 0), 0);

			return `<tr>
      <td>${timestamp}</td>
      <td>${vusers}</td>
      <td>${requests}</td>
      <td>${rate.toFixed(2)}</td>
      <td>${typeof p95 === "number" ? p95.toFixed(1) : p95} ms</td>
      <td>${period_errors}</td>
    </tr>`;
		})
		.join("");

	return `
      <!-- Intermediate Results -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">Intermediate Results by Time Period</h2>
          ${generate_info_icon(explanations.intermediate_results.description)}
        </div>
        <div class="section-container">
          <div class="overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>VUsers Created</th>
                  <th>Requests</th>
                  <th>Req/s</th>
                  <th>p95 (ms)</th>
                  <th>Errors</th>
                </tr>
              </thead>
              <tbody>
                ${intermediate_rows}
              </tbody>
            </table>
          </div>
        </div>
      </section>`;
}

/**
 * Generate Web Vitals section for UI/Playwright tests
 */
export function generate_web_vitals(summaries) {
	// Check if Web Vitals data exists
	const webVitalsKeys = Object.keys(summaries || {}).filter((key) =>
		key.includes("browser.page."),
	);

	if (webVitalsKeys.length === 0) {
		return ""; // Skip section if no Web Vitals data
	}

	// Find the first URL's metrics (usually http://localhost:3000/)
	const ttfb = Object.values(summaries).find((v) =>
		Object.keys(summaries).find((k) => k.includes("TTFB")),
	);
	const ttfbKey = Object.keys(summaries).find((k) => k.includes("browser.page.TTFB"));
	const fcpKey = Object.keys(summaries).find((k) => k.includes("browser.page.FCP"));
	const lcpKey = Object.keys(summaries).find((k) => k.includes("browser.page.LCP"));
	const inpKey = Object.keys(summaries).find((k) => k.includes("browser.page.INP"));
	const clsKey = Object.keys(summaries).find((k) => k.includes("browser.page.CLS"));

	const ttfbMetric = summaries[ttfbKey] || {};
	const fcpMetric = summaries[fcpKey] || {};
	const lcpMetric = summaries[lcpKey] || {};
	const inpMetric = summaries[inpKey] || {};
	const clsMetric = summaries[clsKey] || {};

	return `
      <!-- Web Vitals -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">Web Vitals</h2>
          ${generate_info_icon(explanations.web_vitals.description)}
        </div>
        <div class="percentiles-grid">
          <!-- TTFB: Time To First Byte -->
          <div class="percentile-item">
            <div class="label">TTFB (ms)</div>
            <div class="value">${ttfbMetric.mean ? ttfbMetric.mean.toFixed(1) : "N/A"}</div>
            <div class="text-xs text-gray-400">min: ${ttfbMetric.min ? ttfbMetric.min.toFixed(1) : "N/A"}, max: ${ttfbMetric.max ? ttfbMetric.max.toFixed(1) : "N/A"}</div>
          </div>

          <!-- FCP: First Contentful Paint -->
          <div class="percentile-item">
            <div class="label">FCP (ms)</div>
            <div class="value">${fcpMetric.mean ? fcpMetric.mean.toFixed(1) : "N/A"}</div>
            <div class="text-xs text-gray-400">min: ${fcpMetric.min ? fcpMetric.min.toFixed(1) : "N/A"}, max: ${fcpMetric.max ? fcpMetric.max.toFixed(1) : "N/A"}</div>
          </div>

          <!-- LCP: Largest Contentful Paint -->
          <div class="percentile-item">
            <div class="label">LCP (ms)</div>
            <div class="value">${lcpMetric.mean ? lcpMetric.mean.toFixed(1) : "N/A"}</div>
            <div class="text-xs text-gray-400">min: ${lcpMetric.min ? lcpMetric.min.toFixed(1) : "N/A"}, max: ${lcpMetric.max ? lcpMetric.max.toFixed(1) : "N/A"}</div>
          </div>

          <!-- INP: Interaction to Next Paint -->
          <div class="percentile-item">
            <div class="label">INP (ms)</div>
            <div class="value">${inpMetric.mean ? inpMetric.mean.toFixed(1) : "N/A"}</div>
            <div class="text-xs text-gray-400">min: ${inpMetric.min ? inpMetric.min.toFixed(1) : "N/A"}, max: ${inpMetric.max ? inpMetric.max.toFixed(1) : "N/A"}</div>
          </div>

          <!-- CLS: Cumulative Layout Shift -->
          <div class="percentile-item">
            <div class="label">CLS</div>
            <div class="value">${clsMetric.mean ? clsMetric.mean.toFixed(3) : "N/A"}</div>
            <div class="text-xs text-gray-400">min: ${clsMetric.min ? clsMetric.min.toFixed(3) : "N/A"}, max: ${clsMetric.max ? clsMetric.max.toFixed(3) : "N/A"}</div>
          </div>
        </div>
      </section>`;
}

/**
 * Generate Browser Performance section for UI tests
 */
export function generate_browser_metrics(aggregate) {
	const browserPageCodes = {};
	const browserHttpRequests = aggregate.counters["browser.http_requests"] || 0;
	const browserTracesDiscarded = aggregate.counters["browser.traces_discarded"] || 0;

	// Extract all browser.page.codes.* entries
	Object.entries(aggregate.counters).forEach(([key, value]) => {
		if (key.includes("browser.page.codes.")) {
			const code = key.replace("browser.page.codes.", "");
			browserPageCodes[code] = value;
		}
	});

	if (browserHttpRequests === 0 && Object.keys(browserPageCodes).length === 0) {
		return ""; // Skip section if no browser metrics
	}

	const codeRows = Object.entries(browserPageCodes)
		.map(([code, count]) => {
			const isSuccess = code.startsWith("2");
			const badgeClass = isSuccess ? "status-code-success" : "status-code-error";
			return `<tr>
      <td class="font-semibold">${code}</td>
      <td><span class="status-code-badge ${badgeClass}">${count}</span></td>
    </tr>`;
		})
		.join("");

	return `
      <!-- Browser Performance Metrics -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">Browser Performance</h2>
          ${generate_info_icon(explanations.browser_performance.description)}
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="metric-card">
            <div class="metric-label">Browser HTTP Requests</div>
            <div class="metric-value">${browserHttpRequests.toLocaleString()}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Traces Discarded</div>
            <div class="metric-value">${browserTracesDiscarded.toLocaleString()}</div>
          </div>
        </div>

        ${
			codeRows
				? `
        <div class="section-container mt-4">
          <h3 class="font-semibold text-gray-100 mb-3">Browser Response Codes</h3>
          <div class="overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>Status Code</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                ${codeRows}
              </tbody>
            </table>
          </div>
        </div>`
				: ""
		}
      </section>`;
}

/**
 * Generate screenshots section with lightbox
 */
export function generate_screenshots_section(screenshots) {
	if (!screenshots || screenshots.length === 0) {
		return ""; // Skip if no screenshots
	}

	const screenshot_thumbnails = screenshots
		.map(
			(screenshot, index) => `
			<div class="screenshot-item" onclick="window.openLightbox(${index})">
				<img src="${screenshot}" alt="Screenshot ${index + 1}" class="screenshot-thumb">
				<div class="screenshot-overlay">
					<span class="text-white">View</span>
				</div>
			</div>
		`,
		)
		.join("");

	const screenshot_gallery = screenshots
		.map(
			(screenshot, index) => `
			<div class="lightbox-slide fade" id="slide-${index}">
				<img src="${screenshot}" class="lightbox-image">
				<span class="lightbox-close" onclick="window.closeLightbox()">&times;</span>
				<span class="lightbox-caption">Screenshot ${index + 1}</span>
			</div>
		`,
		)
		.join("");

	return `
      <!-- Screenshots Section -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">Screenshots Gallery</h2>
          <span class="info-icon" title="Visual evidence captured during test execution. Click on any screenshot to view in full size.">
			<svg class="info-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
				<circle cx="8.5" cy="8.5" r="1.5"></circle>
				<polyline points="21 15 16 10 5 21"></polyline>
			</svg>
		</span>
        </div>
        <div class="screenshots-grid">
          ${screenshot_thumbnails}
        </div>
      </section>

      <!-- Lightbox Modal -->
      <div id="lightbox" class="lightbox">
        ${screenshot_gallery}
        <a class="lightbox-prev" onclick="window.changeSlide(-1)">&#10094;</a>
        <a class="lightbox-next" onclick="window.changeSlide(1)">&#10095;</a>
      </div>`;
}
