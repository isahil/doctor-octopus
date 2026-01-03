# CSS Styling Guide for Artillery Reports

## Overview

The CSS styling for Artillery performance reports has been extracted into a separate, reusable stylesheet that makes it easy to customize the look and feel of generated reports.

## File Structure

```
e2e/
├── styles/
│   └── report-styles.css          # Shared CSS stylesheet
├── perf/
│   ├── haiku_perf_report.js       # Report generator (uses external CSS)
│   └── report-utils.js             # Shared utilities module
├── generate_rest_report.js         # REST API report generator
└── CSS_STYLING_GUIDE.md            # This file
```

## Key Files

### `styles/report-styles.css`
Main stylesheet containing all styling for the HTML reports. Organized by component:
- Status badges (success/failed)
- Metric cards
- Tables and data display
- Headers and footers
- Responsive design (mobile, tablet, desktop)

### `perf/report-utils.js`
Shared utilities module with helper functions:
- `copyCSSToOutput(outputDir)` - Copies CSS file to report output directory
- `getHTMLHead(cssFile)` - Returns HTML head with CSS link
- `getHTMLFooter()` - Returns HTML footer
- `formatBytes(bytes)` - Formats bytes to human-readable format
- `ensureOutputDir(outputDir)` - Creates output directory if needed

### `perf/haiku_perf_report.js`
Performance report generator that:
1. Imports utilities from `report-utils.js`
2. Generates HTML content
3. Uses `getHTMLHead()` and `getHTMLFooter()` from utilities
4. Automatically copies `report-styles.css` to output directory
5. Links CSS file in generated HTML

## How It Works

1. **Report Generation**: When you run `haiku_perf_report.js`, it:
   - Parses the JSON data
   - Creates output directory if needed
   - Copies `report-styles.css` to the output directory
   - Generates `index.html` with a link to the CSS file

2. **Styling**: All custom styling is in `report-styles.css`, which:
   - Complements Tailwind CSS (included via CDN)
   - Defines component-specific styles
   - Includes responsive breakpoints
   - Uses semantic CSS classes

## Usage

### Generate a Report
```bash
# Using haiku_perf_report.js
node perf/haiku_perf_report.js <input.json> <output-directory>

# Example
node perf/haiku_perf_report.js test_reports/cards_report.json test_reports/report_output
```

### Customize Styling

To customize report styling:

1. **Edit** `/Users/sahil/Dev/Projects/doctor-octopus/e2e/styles/report-styles.css`
2. **Make changes** to colors, fonts, spacing, etc.
3. **Regenerate reports** - The CSS will be automatically copied to each report output directory

### Common Customizations

#### Change Status Colors
```css
.status-success {
  background-color: #dcfce7;  /* Light green background */
  color: #166534;              /* Dark green text */
  border: 1px solid #86efac;  /* Light green border */
}

.status-failed {
  background-color: #fee2e2;  /* Light red background */
  color: #7f1d1d;              /* Dark red text */
  border: 1px solid #fca5a5;  /* Light red border */
}
```

#### Change Metric Card Styling
```css
.metric-card {
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);  /* Adjust shadow */
}

.metric-value {
  font-size: 28px;    /* Increase/decrease size */
  font-weight: 700;
  color: #1f2937;     /* Change color */
  margin: 8px 0;
}
```

#### Change Table Styling
```css
table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background-color: #f3f4f6;  /* Header background */
  border-bottom: 1px solid #e5e7eb;
}

tbody tr:hover {
  background-color: #f9fafb;  /* Row hover effect */
}
```

## Output Directory Structure

When a report is generated, the output directory contains:

```
report_output/
├── index.html              # Generated HTML report
└── report-styles.css       # Copied CSS stylesheet (auto-generated)
```

Both files are needed to view the report properly. The HTML references the CSS file, so they should stay together.

## Responsive Design

The CSS includes responsive breakpoints:

- **Mobile** (< 480px): Single column layout, smaller fonts
- **Tablet** (480px - 768px): 2-column layouts where appropriate
- **Desktop** (> 768px): Full multi-column layouts

No additional configuration needed - just resize your browser to test responsiveness.

## Maintenance

To add new styling:

1. Edit `styles/report-styles.css`
2. Add your CSS classes
3. Update the JavaScript to use those classes in template literals
4. Test the generated reports

The utilities module (`report-utils.js`) handles CSS distribution, so any changes to the CSS file will automatically be included in all future reports.

## Examples

### View Generated Report
```bash
# Open report in browser (macOS)
open test_reports/report_output/index.html

# Or use a simple HTTP server
cd test_reports/report_output
python3 -m http.server 8000
# Then navigate to http://localhost:8000
```

### Check CSS was Applied
The CSS file should be visible in the generated report directory:
```bash
ls -la test_reports/report_output/
# Output should show both index.html and report-styles.css
```

## Notes

- CSS is copied to each report directory for portability (you can share reports without dependencies)
- Tailwind CSS is still included via CDN for utility classes
- Custom CSS complements Tailwind - they work together
- All styling is self-contained in the CSS file for easy maintenance
