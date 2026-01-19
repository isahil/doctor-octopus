# Guide for Perf Artillery Reports

## Overview

Artillery performance reports are generated dynamically using modular section generators. The system composes multiple report sections (metrics, timing, screenshots, etc.) into a complete HTML report with embedded CSS styling and interactive features like a screenshot lightbox gallery.

## File Structure

```
e2e/perf/reporter/
├── reporter.js              # Main entry point - composes all sections
├── index.js                 # Exports all section generators and utilities
├── report-main.js           # HTML head/footer, header, utility functions
├── report-body.js           # Section generators for all report content
├── explanations.json        # Metadata and tooltips for info icons
├── styles/
│   └── report-styles.css    # Embedded CSS (dark theme, responsive)
└── guide.md                 # This file
```

## Key Files

### `reporter.js`

Main entry point that:

- Parses Artillery JSON report data
- Detects screenshots from filesystem (`screenshots/` directory)
- Composes all report sections
- Embeds CSS directly in HTML output
- Generates complete `index.html` with embedded lightbox script

**Usage:**

```bash
node perf/reporter/reporter.js <input.json> <output-directory>
```

### `report-main.js`

Provides core HTML structure and utilities:

- `get_HTML_head()` - Returns HTML head with embedded CSS
- `get_HTML_footer()` - Returns HTML footer with timestamp
- `generate_header(stats, status, statusIcon)` - Test metadata header with info icon tooltips
- `generate_info_icon(description)` - SVG info icon with hover tooltip
- `format_bytes(bytes)` - Converts bytes to human-readable format

### `report-body.js`

Exports 11+ section generator functions:

- `generate_summary_metrics()` - VUsers, requests, response time, data metrics
- `generate_HTTP_status_codes()` - HTTP status code breakdown table
- `generate_errors_section()` - Error types and counts
- `generate_response_time_percentiles()` - Response time p50-p99 distribution
- `generate_session_length_stats()` - Session duration statistics
- `generate_test_timing_info()` - Test start/end times and duration
- `generate_trace_stats()` - Browser trace collection metrics
- `generate_intermediate_results()` - Time period breakdown table
- `generate_web_vitals()` - Core Web Vitals (TTFB, FCP, LCP, INP, CLS)
- `generate_browser_metrics()` - Browser-specific performance data
- `generate_screenshots_section()` - Responsive screenshot grid with lightbox

### `explanations.json`

Metadata for all report sections:

- Title and description for each section
- Used by info icons to display hover tooltips
- Provides context for users reading reports

### `styles/report-styles.css`

Comprehensive dark theme stylesheet:

- Component-specific styling (metric cards, tables, badges)
- Lightbox modal styles and animations
- Responsive design (mobile, tablet, desktop)
- Tailwind CSS integration via CDN

## Features

### 1. Modular Section Generation

Each report section is a standalone generator function that:

- Takes relevant data parameters
- Returns formatted HTML string
- Includes info icon with tooltip
- Styles itself with CSS classes

### 2. Info Icon Tooltips

Every report section includes an info icon that displays:

- Section description on hover
- Metadata about what data is displayed
- Context for interpreting the metrics

### 3. Screenshot Lightbox Gallery

Automatically detects and displays screenshots:

- Creates responsive grid thumbnail layout
- Click on thumbnail to open full-size image in modal
- Navigate with arrow keys or navigation arrows
- Press ESC or click outside to close
- Wraparound navigation (last image → first image)
- All JavaScript embedded in HTML (no external dependencies)

### 4. Embedded CSS

All styling is embedded directly in HTML:

- Single `index.html` file with no external dependencies
- Dark theme with high contrast colors
- Responsive grid layouts
- Smooth animations and transitions
- Print-friendly design

## How It Works

1. **Input**: User runs `reporter.js` with Artillery JSON report + output directory
2. **Detection**: System checks for `screenshots/` subdirectory with images
3. **Generation**: Each section generator builds its HTML from data
4. **Composition**: All sections combined in `reporter.js` with HTML head/footer
5. **Output**: Single `index.html` file with embedded CSS and lightbox script
6. **Result**: Self-contained report ready to share or view

## Usage

### Generate a Report

```bash
# Using npm script (from e2e directory)
npm run perf-report <input.json> <output-directory>

# Direct node command
node perf/reporter/reporter.js <input.json> <output-directory>

# Example with test report
node perf/reporter/reporter.js ./test_reports/1-4-2026_9-29-03_PM/cards-ui_report.json ./test_reports/1-4-2026_9-29-03_PM
```

### View Generated Report

```bash
# Open in browser (macOS)
open <output-directory>/index.html

# Or use HTTP server
cd <output-directory>
python3 -m http.server 8000
# Navigate to http://localhost:8000
```

### Add Screenshots to Report

```bash
# Create screenshots directory in output folder
mkdir <output-directory>/screenshots

# Copy screenshot images (PNG, JPG, GIF supported)
cp my_screenshots/*.png <output-directory>/screenshots/

# Regenerate report - screenshots will be auto-detected
node perf/reporter/reporter.js <input.json> <output-directory>
```

## Customization

### Add a New Report Section

1. **Create generator function in `report-body.js`:**

```javascript
export function generate_my_section(data) {
	return `
      <section class="mb-8">
        <div class="section-title-container">
          <h2 class="text-xl font-semibold text-gray-100 mb-4">My Section</h2>
          ${generate_info_icon(explanations.my_section.description)}
        </div>
        <!-- Your HTML here -->
      </section>`;
}
```

2. **Add metadata to `explanations.json`:**

```json
{
	"my_section": {
		"description": "What this section displays"
	}
}
```

3. **Export from `index.js`** (already exports all from report-body.js)

4. **Use in `reporter.js`:**

```javascript
import { generate_my_section } from "./index.js";

// In generate_HTML():
${generate_my_section(data)}
```

## Notes

- Single `index.html` is self-contained - no external CSS or JS files needed
- Tailwind CSS is included via CDN for utility classes
- Custom CSS in `report-styles.css` complements Tailwind
- Reports are portable - can be shared as single file
- Print-friendly design works from browser print dialog
