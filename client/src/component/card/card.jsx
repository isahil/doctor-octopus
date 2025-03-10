import React from "react"
import "./card.css"
import config from "../../config.json"
// import { useTerminal } from "../../hooks"

const { SERVER_HOST, SERVER_PORT } = config

function Card({ card, index, filter, setAlert }) {
  const { source } = filter
  const { json_report, root_dir } = card
  const { stats } = json_report
  // const { terminal } = useTerminal()
  const {
    expected,
    flaky,
    skipped,
    unexpected,
    startTime,
    git_branch,
    test_suite,
    environment,
    app,
    duration,
  } = stats // scoreboard values to display
  const project_name = test_suite ?? "N/A"
  const total_tests = expected + flaky + unexpected

  const date = new Date(startTime) // convert startTime to a Date object
  const formatted_date_time = date.toLocaleString() // adjust formatting as needed

  const handle_view_report_click = async () => {
    setAlert((prev) => {
      return { ...prev, opening: true }
    })
    // terminal.write(`\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m Report opening in a new tab on host 'http://localhost:9323'\x1B[0m\r\n`)
    // terminal.write(`\x1B[1;3;31m You\x1B[0m $ `)
    const response = await fetch(
      `http://${SERVER_HOST}:${SERVER_PORT}/card?source=${source}&root_dir=${root_dir}`
    )
    const url = await response.text()

    try {
      const reportWindow = window.open(url, '_blank');
      if (!reportWindow) {
        alert('Popup was blocked. Please allow popups for doctor-octopus website.');
      }
    } catch (error) {
      console.error('Error opening report window:', error);
      alert('Failed to open report window. Please try again.');
    }
    setAlert({ ...alert, opening: false })
  }

  return (
    <div className={`card ${index} ${unexpected === 0 ? "golden" : ""}`}>
      <div className="card-content">
        <div className="card-header">
          <span className="card-title">
            {app ? `${app} -` : ""} {environment}{" "}
          </span>
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
          <button className="score-board" onClick={handle_view_report_click}>
            View
          </button>
        </div>
        <span className="project-name">{project_name}</span>
        <div className="card-footer">
          <span className="branch">{git_branch}</span>
          <span className="duration">{Math.ceil(duration / 1000)} sec</span>
          <span className="time-stamp">{formatted_date_time}</span>
        </div>
      </div>
    </div>
  )
}

export default Card
