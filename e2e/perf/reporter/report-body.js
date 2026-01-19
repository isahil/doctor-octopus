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

	const standard_artillery_prefixes = ["vusers.", "http.", "browser.", "errors.", "plugins."];

	// Extract custom counters (exclude standard Artillery counters)
	const custom_counters = Object.entries(aggregate.counters)
		.filter(([key]) => {
			const is_standard = standard_artillery_prefixes.some((prefix) =>
				key.startsWith(prefix),
			);
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
			<div class="flex items-center justify-between mb-3">
				<div class="text-sm font-semibold text-gray-300">Counters</div>
				${generate_info_icon(explanations.counters.description)}
			</div>
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

	// Extract rates (excluding standard rate prefixes)
	const custom_rates = Object.entries(aggregate.rates || {})
		.filter(([key]) => {
			const is_standard = standard_artillery_prefixes.some((prefix) =>
				key.startsWith(prefix),
			);
			return !is_standard;
		})
		.map(([key, value]) => ({
			name: key.replace(/_/g, " "),
			value: value,
		}));

	const rates_HTML =
		custom_rates.length > 0
			? `
		<div class="rates-section">
			<div class="flex items-center justify-between mb-3">
				<div class="rates-title">Rates</div>
				${generate_info_icon(explanations.rates.description)}
			</div>
			<div class="rates-grid">
				${custom_rates
					.map(
						({ name, value }) => `
				<div class="rate-item">
					<div class="rate-label">${name}</div>
					<div class="rate-value">${typeof value === "number" ? value.toFixed(2) : value} / sec</div>
				</div>
				`,
					)
					.join("")}
			</div>
		</div>`
			: "";

	// Extract custom summaries (exclude standard summary prefixes)
	const custom_summaries = Object.entries(aggregate.summaries || {})
		.filter(([key]) => {
			const is_standard = standard_artillery_prefixes.some((prefix) =>
				key.startsWith(prefix),
			);
			return !is_standard;
		})
		.map(([key, value]) => ({
			name: key.replace(/_/g, " "),
			...value,
		}));

	const custom_histograms_HTML =
		custom_summaries.length > 0
			? `
    <div class="summaries-section">
      <div class="flex items-center justify-between mb-3">
        <div class="summaries-title">Histograms</div>
        ${generate_info_icon(explanations.histograms.description)}
      </div>
      <div class="summaries-grid">
        ${custom_summaries
			.map(
				({ name, min, max, mean, p50, p95, p99 }) => `
        <div class="summary-item">
          <div class="summary-name">${name}</div>
          <div class="summary-stats">
            <div class="summary-stat">
              <span>Min:</span>
              <span class="summary-stat-value">${typeof min === "number" ? (min / 1000).toFixed(2) : "N/A"}s</span>
            </div>
            <div class="summary-stat">
              <span>Mean:</span>
              <span class="summary-stat-value">${typeof mean === "number" ? (mean / 1000).toFixed(2) : "N/A"}s</span>
            </div>
            <div class="summary-stat">
              <span>p50:</span>
              <span class="summary-stat-value">${typeof p50 === "number" ? (p50 / 1000).toFixed(2) : "N/A"}s</span>
            </div>
            <div class="summary-stat">
              <span>p95:</span>
              <span class="summary-stat-value">${typeof p95 === "number" ? (p95 / 1000).toFixed(2) : "N/A"}s</span>
            </div>
            <div class="summary-stat">
              <span>p99:</span>
              <span class="summary-stat-value">${typeof p99 === "number" ? (p99 / 1000).toFixed(2) : "N/A"}s</span>
            </div>
            <div class="summary-stat">
              <span>Max:</span>
              <span class="summary-stat-value">${typeof max === "number" ? (max / 1000).toFixed(2) : "N/A"}s</span>
            </div>
          </div>
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
      <div class="text-xs text-gray-400 mt-2">p99: ${(response_time_summary.p99 || 0).toFixed(1)}ms</div>
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
    ${rates_HTML}
    ${custom_histograms_HTML}
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
              <div class="value">${((response_time_summary.min || 0) / 1000).toFixed(2)}s</div>
            </div>
            <div class="percentile-item">
              <div class="label">p50 (Median)</div>
              <div class="value">${((response_time_summary.p50 || 0) / 1000).toFixed(2)}s</div>
            </div>
            <div class="percentile-item">
              <div class="label">p75</div>
              <div class="value">${((response_time_summary.p75 || 0) / 1000).toFixed(2)}s</div>
            </div>
            <div class="percentile-item">
              <div class="label">p90</div>
              <div class="value">${((response_time_summary.p90 || 0) / 1000).toFixed(2)}s</div>
            </div>
            <div class="percentile-item">
              <div class="label">p95</div>
              <div class="value">${((response_time_summary.p95 || 0) / 1000).toFixed(2)}s</div>
            </div>
            <div class="percentile-item">
              <div class="label">p99</div>
              <div class="value">${((response_time_summary.p99 || 0) / 1000).toFixed(2)}s</div>
            </div>
            <div class="percentile-item">
              <div class="label">Max</div>
              <div class="value">${((response_time_summary.max || 0) / 1000).toFixed(2)}s</div>
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
              <div class="value">${session_length_data.min ? (session_length_data.min / 1000).toFixed(2) : "N/A"}s</div>
            </div>
            <div class="percentile-item">
              <div class="label">p50 (Median)</div>
              <div class="value">${session_length_data.p50 ? (session_length_data.p50 / 1000).toFixed(2) : "N/A"}s</div>
            </div>
            <div class="percentile-item">
              <div class="label">Mean Duration</div>
              <div class="value">${session_length_data.mean ? (session_length_data.mean / 1000).toFixed(2) : "N/A"}s</div>
            </div>
            <div class="percentile-item">
              <div class="label">p95</div>
              <div class="value">${session_length_data.p95 ? (session_length_data.p95 / 1000).toFixed(2) : "N/A"}s</div>
            </div>
            <div class="percentile-item">
              <div class="label">p99</div>
              <div class="value">${session_length_data.p99 ? (session_length_data.p99 / 1000).toFixed(2) : "N/A"}s</div>
            </div>
            <div class="percentile-item">
              <div class="label">Max Duration</div>
              <div class="value">${session_length_data.max ? (session_length_data.max / 1000).toFixed(2) : "N/A"}s</div>
            </div>
          </div>
        </div>
      </section>`;
}

/**
 * Generate intermediate results section
 */
export function generate_intermediate_results(intermediate) {
	// Collect all unique browser.page metrics across all periods
	const browser_page_metrics = new Set();
	intermediate.forEach((period) => {
		Object.keys(period.summaries || {}).forEach((key) => {
			if (key.includes("browser.page.")) {
				const match = key.match(/browser\.page\.(\w+)\./);
				if (match) {
					browser_page_metrics.add(match[1]);
				}
			}
		});
	});
	const sorted_metrics = Array.from(browser_page_metrics).sort();

	// Check if HTTP data is available
	const has_http_data = intermediate.some(
		(period) =>
			period.counters?.["http.requests"] ||
			period.rates?.["http.request_rate"] ||
			period.summaries?.["http.response_time"],
	);

	const intermediate_rows = intermediate
		.map((period) => {
			const timestamp = new Date(parseInt(period.period)).toLocaleString();
			const vusers = period.counters["vusers.created"] || 0;

			let row = `<tr>
      <td>${timestamp}</td>
      <td>${vusers}</td>`;

			// Add HTTP columns only if data is available
			if (has_http_data) {
				const requests = period.counters["http.requests"] || 0;
				const rate = period.rates["http.request_rate"] || 0;
				const p95 = period.summaries?.["http.response_time"]?.p95 || "0";
				row += `
      <td>${requests}</td>
      <td>${rate.toFixed(2)}</td>
      <td>${typeof p95 === "number" ? (p95 / 1000).toFixed(2) : p95}s</td>`;
			}

			// Add browser.page metrics dynamically
			sorted_metrics.forEach((metric) => {
				const url_suffix =
					Object.keys(period.summaries || {})
						.find((key) => key.startsWith(`browser.page.${metric}.`))
						?.split("browser.page." + metric + ".")[1] || "";
				const key = `browser.page.${metric}.${url_suffix}`;
				const value = period.summaries?.[key]?.p95;
				const display = typeof value === "number" ? (value / 1000).toFixed(2) : "N/A";
				row += `
      <td>${display}${typeof value === "number" ? "s" : ""}</td>`;
			});

			const period_errors = Object.keys(period.counters)
				.filter((key) => key.includes("errors"))
				.reduce((sum, key) => sum + (period.counters[key] || 0), 0);
			row += `
      <td>${period_errors}</td>
    </tr>`;
			return row;
		})
		.join("");

	// Build table header dynamically
	let table_header = `
                <tr>
                  <th>Timestamp</th>
                  <th>VUsers Created</th>`;
	if (has_http_data) {
		table_header += `
                  <th>Requests</th>
                  <th>Req/s</th>
                  <th>p95 HTTP (s)</th>`;
	}
	sorted_metrics.forEach((metric) => {
		table_header += `
                  <th>${metric} (s)</th>`;
	});
	table_header += `
                  <th>Errors</th>
                </tr>`;

	return `
      <!-- Intermediate Results -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">Intermediate Results by Time Period</h2>
          ${generate_info_icon(explanations.intermediate_results.description)}
        </div>
        <div class="intermediate section-container">
          <div class="overflow-x-auto">
            <table>
              <thead>
                ${table_header}
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
	const web_vitals_keys = Object.keys(summaries || {}).filter((key) =>
		key.includes("browser.page."),
	);

	if (web_vitals_keys.length === 0) {
		return ""; // Skip section if no Web Vitals data
	}

	// Extract unique URLs from Web Vitals keys
	const url_set = new Set();
	web_vitals_keys.forEach((key) => {
		const match = key.match(/browser\.page\.\w+\.(.*)/);
		if (match) {
			url_set.add(match[1]);
		}
	});

	const urls = Array.from(url_set);

	const url_sections = urls
		.map((url) => {
			const ttfb_key = `browser.page.TTFB.${url}`;
			const fcp_key = `browser.page.FCP.${url}`;
			const lcp_key = `browser.page.LCP.${url}`;
			const inp_key = `browser.page.INP.${url}`;
			const cls_key = `browser.page.CLS.${url}`;
			const ttfb_metric = summaries[ttfb_key] || {};
			const fcp_metric = summaries[fcp_key] || {};
			const lcp_metric = summaries[lcp_key] || {};
			const inp_metric = summaries[inp_key] || {};
			const cls_metric = summaries[cls_key] || {};
			return `
        <div class="url-section mb-6">
          <h3 class="text-sm font-semibold text-gray-300 mb-4 px-1">${url}</h3>
          <div class="percentiles-grid">
            <!-- TTFB: Time To First Byte -->
            <div class="percentile-item">
              <div class="label">TTFB (ms)</div>
              <div class="value">${ttfb_metric.mean ? ttfb_metric.mean.toFixed(1) : "N/A"}</div>
              <div class="text-xs text-gray-400">min: ${ttfb_metric.min ? ttfb_metric.min.toFixed(1) : "N/A"}, max: ${ttfb_metric.max ? ttfb_metric.max.toFixed(1) : "N/A"}</div>
            </div>

            <!-- FCP: First Contentful Paint -->
            <div class="percentile-item">
              <div class="label">FCP (ms)</div>
              <div class="value">${fcp_metric.mean ? fcp_metric.mean.toFixed(1) : "N/A"}</div>
              <div class="text-xs text-gray-400">min: ${fcp_metric.min ? fcp_metric.min.toFixed(1) : "N/A"}, max: ${fcp_metric.max ? fcp_metric.max.toFixed(1) : "N/A"}</div>
            </div>

            <!-- LCP: Largest Contentful Paint -->
            <div class="percentile-item">
              <div class="label">LCP (ms)</div>
              <div class="value">${lcp_metric.mean ? lcp_metric.mean.toFixed(1) : "N/A"}</div>
              <div class="text-xs text-gray-400">min: ${lcp_metric.min ? lcp_metric.min.toFixed(1) : "N/A"}, max: ${lcp_metric.max ? lcp_metric.max.toFixed(1) : "N/A"}</div>
            </div>

            <!-- INP: Interaction to Next Paint -->
            <div class="percentile-item">
              <div class="label">INP (ms)</div>
              <div class="value">${inp_metric.mean ? inp_metric.mean.toFixed(1) : "N/A"}</div>
              <div class="text-xs text-gray-400">min: ${inp_metric.min ? inp_metric.min.toFixed(1) : "N/A"}, max: ${inp_metric.max ? inp_metric.max.toFixed(1) : "N/A"}</div>
            </div>

            <!-- CLS: Cumulative Layout Shift -->
            <div class="percentile-item">
              <div class="label">CLS</div>
              <div class="value">${cls_metric.mean ? cls_metric.mean.toFixed(3) : "N/A"}</div>
              <div class="text-xs text-gray-400">min: ${cls_metric.min ? cls_metric.min.toFixed(3) : "N/A"}, max: ${cls_metric.max ? cls_metric.max.toFixed(3) : "N/A"}</div>
            </div>
          </div>
        </div>`;
		})
		.join("");

	return `
      <!-- Web Vitals -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">Web Vitals</h2>
          ${generate_info_icon(explanations.web_vitals.description)}
        </div>
        ${url_sections}
      </section>`;
}

/**
 * Generate Browser Performance section for UI tests
 */
export function generate_browser_metrics(aggregate) {
	const browser_page_codes = {};
	const browser_http_requests = aggregate.counters["browser.http_requests"] || 0;
	const browser_traces_collected = aggregate.counters["browser.traces_collected"] || 0;
	const browser_traces_discarded = aggregate.counters["browser.traces_discarded"] || 0;

	// Extract all browser.page.codes.* entries
	Object.entries(aggregate.counters).forEach(([key, value]) => {
		if (key.includes("browser.page.codes.")) {
			const code = key.replace("browser.page.codes.", "");
			browser_page_codes[code] = value;
		}
	});

	if (browser_http_requests === 0 && Object.keys(browser_page_codes).length === 0) {
		return ""; // Skip section if no browser metrics
	}

	const codeRows = Object.entries(browser_page_codes)
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
            <div class="metric-value">${browser_http_requests.toLocaleString()}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Traces Collected</div>
            <div class="metric-value">${browser_traces_collected.toLocaleString()}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Traces Discarded</div>
            <div class="metric-value">${browser_traces_discarded.toLocaleString()}</div>
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
 * Generate test scenario section with browser steps
 */
export function generate_test_scenario(summaries) {
	// Extract browser.step entries
	const browser_steps = Object.entries(summaries || {})
		.filter(([key]) => key.startsWith("browser.step."))
		.map(([key, value]) => ({
			step_name: key.replace("browser.step.", ""),
			...value,
		}));

	if (browser_steps.length === 0) {
		return ""; // Skip if no browser steps
	}

	const step_rows = browser_steps
		.map((step, index) => {
			return `
      <div class="step-item">
        <div class="step-number">${index + 1}</div>
        <div class="step-details">
          <div class="step-name">${step.step_name}</div>
          <div class="step-metrics">
            <div class="metric-row">
              <span class="metric-label">Min:</span>
              <span class="metric-value">${step.min ? (step.min / 1000).toFixed(2) : "N/A"}s</span>
              <span class="metric-label">Mean:</span>
              <span class="metric-value">${step.mean ? (step.mean / 1000).toFixed(2) : "N/A"}s</span>
              <span class="metric-label">p95:</span>
              <span class="metric-value">${step.p95 ? (step.p95 / 1000).toFixed(2) : "N/A"}s</span>
              <span class="metric-label">Max:</span>
              <span class="metric-value">${step.max ? (step.max / 1000).toFixed(2) : "N/A"}s</span>
            </div>
          </div>
        </div>
      </div>`;
		})
		.join("");

	return `
      <!-- Test Scenario -->
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">Test Scenario</h2>
          ${generate_info_icon(explanations.test_scenarios.description)}
        </div>
        <div class="section-container test-scenario-container">
          ${step_rows}
        </div>
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
