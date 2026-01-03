import { formatBytes } from "./index.js";
/**
 * Generate summary metrics section
 */
export function generateSummaryMetrics(
	aggregate,
	responseTimeSummary,
	httpDownloadedBytes,
	httpResponses,
	requestRate
) {
	const totalVusers = aggregate.counters["vusers.created"] || 0;
	const completedVusers = aggregate.counters["vusers.completed"] || 0;
	const failedVusers = aggregate.counters["vusers.failed"] || 0;
	const httpRequests = aggregate.counters["http.requests"] || 0;

	return `
      <!-- Summary Metrics -->
      <section class="mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Summary</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Virtual Users -->
          <div class="metric-card bg-white border border-gray-200">
            <div class="metric-label">Virtual Users Created</div>
            <div class="metric-value">${totalVusers.toLocaleString()}</div>
            <div class="text-xs text-gray-600 mt-2">
              <span class="text-green-600 font-semibold">${completedVusers}</span> completed, 
              <span class="text-red-600 font-semibold">${failedVusers}</span> failed
            </div>
          </div>

          <!-- HTTP Requests -->
          <div class="metric-card bg-white border border-gray-200">
            <div class="metric-label">HTTP Requests</div>
            <div class="metric-value">${httpRequests.toLocaleString()}</div>
            <div class="text-xs text-gray-600 mt-2">${requestRate.toFixed(2)} req/s average</div>
          </div>

          <!-- Response Time -->
          <div class="metric-card bg-white border border-gray-200">
            <div class="metric-label">Avg Response Time</div>
            <div class="metric-value">${(responseTimeSummary.mean || 0).toFixed(1)}<span class="text-sm">ms</span></div>
            <div class="text-xs text-gray-600 mt-2">p95: ${(responseTimeSummary.p95 || 0).toFixed(1)}ms</div>
          </div>

          <!-- Downloaded Data -->
          <div class="metric-card bg-white border border-gray-200">
            <div class="metric-label">Data Downloaded</div>
            <div class="metric-value text-lg">${formatBytes(httpDownloadedBytes)}</div>
            <div class="text-xs text-gray-600 mt-2">${httpResponses} responses</div>
          </div>
        </div>
      </section>`;
}

/**
 * Generate HTTP status codes section
 */
export function generateHTTPStatusCodes(aggregate, httpResponses) {
	const statusCodes = Object.keys(aggregate.counters)
		.filter((key) => key.startsWith("http.codes."))
		.map((key) => ({
			code: key.replace("http.codes.", ""),
			count: aggregate.counters[key],
		}));

	return `
      <!-- HTTP Status Codes -->
      <section class="mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">HTTP Status Codes</h2>
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table class="w-full">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status Code</th>
                <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Count</th>
                <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Percentage</th>
              </tr>
            </thead>
            <tbody>
              ${statusCodes
					.map(({ code, count }) => {
						const percentage = ((count / httpResponses) * 100).toFixed(1);
						const isSuccess = code.startsWith("2");
						return `<tr class="border-b border-gray-200 hover:bg-gray-50">
                  <td class="px-6 py-3">
                    <span class="px-2.5 py-0.5 rounded-full text-sm font-semibold ${isSuccess ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}">
                      ${code}
                    </span>
                  </td>
                  <td class="px-6 py-3 font-semibold text-gray-900">${count.toLocaleString()}</td>
                  <td class="px-6 py-3 text-gray-600">${percentage}%</td>
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
export function generateErrorsSection(aggregate) {
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
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Errors</h2>
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table class="w-full">
            <thead class="bg-red-50 border-b border-gray-200">
              <tr>
                <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Error Type</th>
                <th class="px-6 py-3 text-left text-sm font-semibold text-gray-900">Count</th>
              </tr>
            </thead>
            <tbody>
              ${Object.entries(errors)
					.map(
						([type, count]) => `
              <tr class="border-b border-gray-200 hover:bg-red-50">
                <td class="px-6 py-3 font-medium text-gray-900">${type}</td>
                <td class="px-6 py-3 font-semibold text-red-600">${count.toLocaleString()}</td>
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
export function generateResponseTimePercentiles(responseTimeSummary) {
	return `
      <!-- Response Time Percentiles -->
      <section class="mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Response Time Percentiles</h2>
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <div class="text-sm text-gray-600">Min</div>
              <div class="text-2xl font-bold text-gray-900">${(responseTimeSummary.min || 0).toFixed(1)}ms</div>
            </div>
            <div>
              <div class="text-sm text-gray-600">p50 (Median)</div>
              <div class="text-2xl font-bold text-gray-900">${(responseTimeSummary.p50 || 0).toFixed(1)}ms</div>
            </div>
            <div>
              <div class="text-sm text-gray-600">p95</div>
              <div class="text-2xl font-bold text-gray-900">${(responseTimeSummary.p95 || 0).toFixed(1)}ms</div>
            </div>
            <div>
              <div class="text-sm text-gray-600">Max</div>
              <div class="text-2xl font-bold text-gray-900">${(responseTimeSummary.max || 0).toFixed(1)}ms</div>
            </div>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-6 mt-6 pt-6 border-t border-gray-200">
            <div>
              <div class="text-sm text-gray-600">p75</div>
              <div class="text-xl font-bold text-gray-900">${(responseTimeSummary.p75 || 0).toFixed(1)}ms</div>
            </div>
            <div>
              <div class="text-sm text-gray-600">p90</div>
              <div class="text-xl font-bold text-gray-900">${(responseTimeSummary.p90 || 0).toFixed(1)}ms</div>
            </div>
            <div>
              <div class="text-sm text-gray-600">p99</div>
              <div class="text-xl font-bold text-gray-900">${(responseTimeSummary.p99 || 0).toFixed(1)}ms</div>
            </div>
          </div>
        </div>
      </section>`;
}

/**
 * Generate intermediate results section
 */
export function generateIntermediateResults(intermediate) {
	const intermediateRows = intermediate
		.map((period) => {
			const timestamp = new Date(parseInt(period.period)).toLocaleString();
			const vusers = period.counters["vusers.created"] || 0;
			const requests = period.counters["http.requests"] || 0;
			const rate = period.rates["http.request_rate"] || 0;
			const p95 = period.summaries?.["http.response_time"]?.p95 || "N/A";
			const periodErrors = Object.keys(period.counters)
				.filter((key) => key.includes("errors"))
				.reduce((sum, key) => sum + (period.counters[key] || 0), 0);

			return `<tr>
      <td class="border border-gray-300 px-4 py-2 text-sm">${timestamp}</td>
      <td class="border border-gray-300 px-4 py-2 text-sm">${vusers}</td>
      <td class="border border-gray-300 px-4 py-2 text-sm">${requests}</td>
      <td class="border border-gray-300 px-4 py-2 text-sm">${rate.toFixed(2)}</td>
      <td class="border border-gray-300 px-4 py-2 text-sm">${typeof p95 === "number" ? p95.toFixed(1) : p95} ms</td>
      <td class="border border-gray-300 px-4 py-2 text-sm">${periodErrors}</td>
    </tr>`;
		})
		.join("");

	return `
      <!-- Intermediate Results -->
      <section class="mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Intermediate Results by Time Period</h2>
        <div class="bg-white rounded-lg border border-gray-200 overflow-x-auto">
          <table class="w-full text-xs">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="border border-gray-300 px-4 py-2 text-left font-semibold">Timestamp</th>
                <th class="border border-gray-300 px-4 py-2 text-left font-semibold">VUsers Created</th>
                <th class="border border-gray-300 px-4 py-2 text-left font-semibold">Requests</th>
                <th class="border border-gray-300 px-4 py-2 text-left font-semibold">Req/s</th>
                <th class="border border-gray-300 px-4 py-2 text-left font-semibold">p95 (ms)</th>
                <th class="border border-gray-300 px-4 py-2 text-left font-semibold">Errors</th>
              </tr>
            </thead>
            <tbody>
              ${intermediateRows}
            </tbody>
          </table>
        </div>
      </section>`;
}
