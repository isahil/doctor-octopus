import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Read and embed CSS stylesheet inline in HTML
 */
export function get_embedded_CSS() {
	const css_source_path = path.join(__dirname, ".", "styles", "report-styles.css");

	try {
		if (fs.existsSync(css_source_path)) {
			const cssContent = fs.readFileSync(css_source_path, "utf8");
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
export function get_HTML_head() {
	const css_content = get_embedded_CSS();
	const css_tag = css_content ? `<style>\n${css_content}\n</style>` : "";

	return `<!DOCTYPE html>
          <html lang="en">
              <head>
                  <meta charset="UTF-8">
                  <meta name="viewport" content="width=device-width, initial-scale=1.0">
                  <title>DO Report</title>
                  <script src="https://cdn.tailwindcss.com"></script>
                  <script>
                      tailwindConfig = {
                          darkMode: 'class'
                      }
                  </script>
                  ${css_tag}
              </head>
              <body class="bg-gray-900 text-gray-100 dark">
                  <div class="min-h-screen">
        `;
}

/**
 * Generate header section with status and metadata
 */
export function generate_header(stats, status, statusIcon) {
	const grafana_url = stats.app_grafana_url;
	return `
    <!-- Header -->
    <header class="bg-gray-800 border-b border-gray-700">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-2xl font-bold text-gray-100">Doctor Octopus Perf Report</h1>
          <div class="status-badge ${status === "SUCCEEDED" ? "status-success" : "status-failed"}">
            ${statusIcon} ${status}
          </div>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
          <div>
            <span class="text-gray-400">Test Suite:</span>
            <p class="font-semibold text-gray-100">${stats.test_suite || "N/A"}</p>
          </div>
          <div>
            <span class="text-gray-400">Environment:</span>
            <p class="font-semibold text-gray-100">${stats.environment || "N/A"}</p>
          </div>
          <div>
            <span class="text-gray-400">Product:</span>
            <p class="font-semibold text-gray-100">${stats.product || "N/A"}</p>
          </div>
          <div>
            <span class="text-gray-400">Branch:</span>
            <p class="font-semibold text-gray-100">${stats.git_branch || "N/A"}</p>
          </div>
          <div>
            <span class="text-gray-400">User:</span>
            <p class="font-semibold text-gray-100">${stats.username || "N/A"}</p>
          </div>
          <div>
            <span class="text-gray-400">Protocol:</span>
            <p class="font-semibold text-gray-100">${stats.protocol || "N/A"}</p>
          </div>
          <div>
            <span class="text-gray-400">Grafana:</span>
            ${grafana_url 
              ? `<a class="grafana-button" href="${grafana_url}" target="_blank" rel="noopener noreferrer">📊 View Dashboard</a>`
              : `<a class="font-semibold text-gray-100">${grafana_url}</a>`}
        </div>
      </div>
    </header>`;
}

/**
 * Get HTML footer
 */
export function get_HTML_footer() {
	return `    <!-- Footer -->
                <footer class="bg-gray-800 border-t border-gray-700 mt-12 py-6">
                    <div class="max-w-7xl mx-auto px-6 text-center text-sm text-gray-400">
                        <p>Generated on ${new Date().toLocaleString()}</p>
                        <p>Developer: Imran Sahil</p>
                    </div>
                </footer>
            </div>
        </body>
    </html>`;
}

/**
 * Format bytes to human-readable format
 */
export function format_bytes(bytes) {
	if (bytes === 0) return "0 B";
	const k = 1024;
	const sizes = ["B", "KB", "MB", "GB"];
	const i = Math.floor(Math.log(bytes) / Math.log(k));
	return (bytes / Math.pow(k, i)).toFixed(2) + " " + sizes[i];
}

/**
 * Generate info icon with tooltip
 */
export function generate_info_icon(explanation) {
	return `<span class="info-icon" title="${explanation}">
		<svg class="info-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
			<circle cx="12" cy="12" r="10"></circle>
			<line x1="12" y1="16" x2="12" y2="12"></line>
			<line x1="12" y1="8" x2="12.01" y2="8"></line>
		</svg>
	</span>`;
}

export function html_utils() {
	return `
  <script>
      // Initialize lightbox functionality for screenshots
      window.currentSlide = 0;
      const slides = document.querySelectorAll('.lightbox-slide');

      window.openLightbox = function(index) {
        window.currentSlide = index;
        document.getElementById('lightbox').style.display = 'block';
        window.showSlide(window.currentSlide);
      };

      window.closeLightbox = function() {
        document.getElementById('lightbox').style.display = 'none';
      };

      window.changeSlide = function(n) {
        window.currentSlide += n;
        if (window.currentSlide >= slides.length) window.currentSlide = 0;
        if (window.currentSlide < 0) window.currentSlide = slides.length - 1;
        window.showSlide(window.currentSlide);
      };

      window.showSlide = function(n) {
        slides.forEach(slide => slide.classList.remove('show'));
        if (slides[n]) slides[n].classList.add('show');
      };

      // Close lightbox when clicking outside
      const lightbox = document.getElementById('lightbox');
      if (lightbox) {
        lightbox.addEventListener('click', function(e) {
          if (e.target === this) window.closeLightbox();
        });

        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
          if (lightbox.style.display === 'block') {
            if (e.key === 'Escape') window.closeLightbox();
            if (e.key === 'ArrowLeft') window.changeSlide(-1);
            if (e.key === 'ArrowRight') window.changeSlide(1);
          }
        });
      }
    </script>`;
}
