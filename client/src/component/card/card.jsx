import "./card.css"
import { github_icon, grafana_icon } from "../../util/icons"

const { VITE_MAIN_SERVER_HOST, VITE_MAIN_SERVER_PORT } = import.meta.env

function Card({ card, index, filter, setAlert }) {
  const { source, protocol } = filter
  const { json_report, root_dir } = card
  const { stats, ci, aggregate } = json_report
  const {
    expected = 0,
    flaky = 0,
    skipped = 0,
    unexpected = 0,
    startTime = "",
    git_branch = "n_a",
    test_suite = "n_a",
    environment = "n_a",
    app = "n_a",
  } = stats // scoreboard values

  // Calculate duration: for perf protocol, use aggregate timestamps; otherwise use stats.duration
  let duration = 0
  if (protocol === "perf" && !startTime) {
    duration = (aggregate.lastMetricAt - aggregate.firstMetricAt)
  } else {
    duration = stats?.duration || 0
  }

  const project_name = test_suite ?? "N/A"
  const total_tests = expected + flaky + unexpected
  const date = new Date(startTime)
  const formatted_date_time = date.toLocaleString() // formatting
  const run_url = ci?.run_url ?? "" // GitHub Action run URL
  const grafana_url = stats?.app_grafana_url // Grafana Dashboard URL
  const sdet = ci?.sdet ?? ""

  const handle_view_report_click = async () => {
    setAlert((prev) => {
      return { ...prev, opening: true }
    })

    const server_url = `http://${VITE_MAIN_SERVER_HOST}:${VITE_MAIN_SERVER_PORT}`
    const response = await fetch(`${server_url}/card?source=${source}&root_dir=${root_dir}`)
    const report_path = await response.text()
    const full_report_url = `${server_url}${report_path}`
    try {
      const report_window = window.open(full_report_url, "_blank")
      if (!report_window) {
        alert("Popup was blocked. Please allow popups for doctor-octopus website.")
      }
    } catch (error) {
      console.error("Error opening report window:", error)
      alert("Failed to open report window. Please try again.")
    }
    setAlert({ ...alert, opening: false })
  }

  const handle_github_click = (e) => {
    console.log(`GitHub button clicked.. url: ${run_url}`)
    e.stopPropagation()
    if (run_url) {
      window.open(run_url, "_blank")
    }
  }

  const handle_grafana_click = (e) => {
    // const valid_url = grafana_url.startsWith("http") ? grafana_url : ""
    console.log(`Grafana button clicked.. url: ${grafana_url}`)
    e.stopPropagation()
    if (grafana_url) {
      window.open(grafana_url, "_blank")
    } else {
      alert("Grafana URL is not available for this report.")
    }
  }

  return (
    <div className={`card ${index} ${unexpected === 0 ? "golden" : ""}`}>
      <div className="card-content">
        <div className="card-header">
          <span className="sdet-name">{sdet}</span>
          <span className="project-name">{project_name}</span>
        </div>
        <div className="score-board-container ">
          <div className="score-board all">
            All
            <span className="score"> {total_tests} </span>
          </div>
          <div className="score-board pass" style={{ color: expected > 0 ? "#2fd711" : "inherit" }}>
            Passed
            <span className="score"> {expected} </span>
          </div>
          <div className={`score-board fail`} style={{ color: unexpected > 0 ? "red" : "inherit" }}>
            Failed
            <span className="score"> {unexpected} </span>
          </div>
          <div className="score-board flaky" style={{ color: flaky > 0 ? "yellow" : "inherit" }}>
            Flaky
            <span className="score"> {flaky} </span>
          </div>
          <div
            className="score-board skipped"
            style={{ color: skipped > 0 ? "orange" : "inherit" }}
          >
            Skipped
            <span className="score"> {skipped} </span>
          </div>
          <button
            className="score-board"
            onClick={handle_view_report_click}
            title="View Report"
            aria-label="View Report"
          >
            View
          </button>
        </div>
        <span className="card-title">
          {app ? `${app} -` : ""} {environment}{" "}
        </span>
        <div className="card-footer">
          <span className="branch">{git_branch}</span>
          <span className="duration">{Math.ceil(duration / 1000)} sec</span>
          <span className="time-stamp">{formatted_date_time}</span>
        </div>
        <div className="github-info">
          {run_url && (
            <button
              className="github-icon-button"
              href={run_url}
              onClick={handle_github_click}
              title="View GitHub Workflow"
              aria-label="View GitHub Workflow"
            >
              {github_icon(18, 18)}
            </button>
          )}
        </div>
        <div className="grafana-info">
          {grafana_url && (
            <button
              className="grafana-icon-button"
              href={grafana_url}
              onClick={handle_grafana_click}
              title="View Grafana Dashboard"
              aria-label="View Grafana Dashboard"
            >
              {grafana_icon(18, 18)}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default Card
