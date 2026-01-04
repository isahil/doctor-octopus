import { format_bytes } from "./index.js";

/**
 * Generate summary metrics section
 */
export function generate_summary_metrics(
	aggregate,
	responseTimeSummary,
	httpDownloadedBytes,
	httpResponses,
	requestRate
) {
	const total_vusers = aggregate.counters["vusers.created"] || 0;
	const completed_vusers = aggregate.counters["vusers.completed"] || 0;
	const failed_vusers = aggregate.counters["vusers.failed"] || 0;
	const http_requests = aggregate.counters["http.requests"] || 0;

	return `
      <!-- Summary Metrics -->
      <section class="mb-8">
        <h2 class="text-xl font-semibold text-gray-100 mb-4">Summary Metrics</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Virtual Users -->
          <div class="metric-card">
            <div class="metric-label">Virtual Users Created</div>
            <div class="metric-value">${total_vusers.toLocaleString()}</div>
            <div class="text-xs text-gray-400 mt-2">
              <span class="success-indicator font-semibold">${completed_vusers}</span> completed, 
              <span class="failed-indicator font-semibold">${failed_vusers}</span> failed
            </div>
          </div>

          <!-- HTTP Requests -->
          <div class="metric-card">
            <div class="metric-label">HTTP Requests</div>
            <div class="metric-value">${http_requests.toLocaleString()}</div>
            <div class="text-xs text-gray-400 mt-2">${requestRate.toFixed(2)} req/s average</div>
          </div>

          <!-- Response Time -->
          <div class="metric-card">
            <div class="metric-label">Avg Response Time</div>
            <div class="metric-value">${(responseTimeSummary.mean || 0).toFixed(1)}<span class="text-sm">ms</span></div>
            <div class="text-xs text-gray-400 mt-2">p95: ${(responseTimeSummary.p95 || 0).toFixed(1)}ms</div>
          </div>

          <!-- Downloaded Data -->
          <div class="metric-card">
            <div class="metric-label">Data Downloaded</div>
            <div class="metric-value text-lg">${format_bytes(httpDownloadedBytes)}</div>
            <div class="text-xs text-gray-400 mt-2">${httpResponses} responses</div>
          </div>
        </div>
      </section>`;
}

/**
 * Generate HTTP status codes section
 */
export function generate_HTTP_status_codes(aggregate, httpResponses) {
	const status_codes = Object.keys(aggregate.counters)
		.filter((key) => key.startsWith("http.codes."))
		.map((key) => ({
			code: key.replace("http.codes.", ""),
			count: aggregate.counters[key],
		}));

	return `
      <!-- HTTP Status Codes -->
      <section class="mb-8">
        <h2 class="text-xl font-semibold text-gray-100 mb-4">HTTP Status Codes</h2>
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
						const percentage = ((count / httpResponses) * 100).toFixed(1);
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
        <h2 class="text-xl font-semibold text-gray-100 mb-4">Errors</h2>
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
              `
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
export function generate_response_time_percentiles(responseTimeSummary) {
	return `
      <!-- Response Time Percentiles -->
      <section class="mb-8">
        <h2 class="text-xl font-semibold text-gray-100 mb-4">Response Time Percentiles</h2>
        <div class="section-container">
          <div class="percentiles-grid">
            <div class="percentile-item">
              <div class="label">Min</div>
              <div class="value">${(responseTimeSummary.min || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p50 (Median)</div>
              <div class="value">${(responseTimeSummary.p50 || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p75</div>
              <div class="value">${(responseTimeSummary.p75 || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p90</div>
              <div class="value">${(responseTimeSummary.p90 || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p95</div>
              <div class="value">${(responseTimeSummary.p95 || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">p99</div>
              <div class="value">${(responseTimeSummary.p99 || 0).toFixed(1)}ms</div>
            </div>
            <div class="percentile-item">
              <div class="label">Max</div>
              <div class="value">${(responseTimeSummary.max || 0).toFixed(1)}ms</div>
            </div>
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
        <h2 class="text-xl font-semibold text-gray-100 mb-4">Intermediate Results by Time Period</h2>
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
		key.includes("browser.page.")
	);

	if (webVitalsKeys.length === 0) {
		return ""; // Skip section if no Web Vitals data
	}

	// Find the first URL's metrics (usually http://localhost:3000/)
	const ttfb = Object.values(summaries).find((v) =>
		Object.keys(summaries).find((k) => k.includes("TTFB"))
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
        <h2 class="text-xl font-semibold text-gray-100 mb-4">Web Vitals</h2>
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
        <h2 class="text-xl font-semibold text-gray-100 mb-4">Browser Performance</h2>
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
