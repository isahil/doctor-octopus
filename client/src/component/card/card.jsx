import React from "react";
import "./card.css";
import { SERVER_HOST, SERVER_PORT } from "../../index";

function Card({ source, card, index }) {
  const { json_report, html_report } = card;
  const { stats, config } = json_report;
  // console.log(`Stats: ${JSON.stringify(stats)} \n${html_report.length === 0 ? "No HTML Report" : "Yes HTML Report"}`);
  const { expected, flaky, skipped, unexpected, startTime } = stats; // scoreboard values to display
  const project_name = config.projects[0].id; // get the project name for the card title
  const total_tests = expected + flaky + unexpected;

  const date = new Date(startTime); // convert startTime to a Date object
  const formatted_date_time = date.toLocaleString(); // adjust formatting as needed

  const handle_view_report_click = async () => {
    console.log(`Viewing html report: ${html_report}`);
    const response = await fetch(
      `http://${SERVER_HOST}:${SERVER_PORT}/report?source=${source}&html=${html_report}`
    );
    const html_report_text = await response.text();

    const new_window = window.open("", "_blank"); // open a new window to display the clicked report
    if (new_window) {
      new_window.document.open();
      new_window.document.write(html_report_text);
      new_window.document.close();
    } else alert("Please allow popups for this website");
  };

  return (
    <div className={`card ${index}`}>
      <div className="card-content">
        <div className="score-board-container ">
          <div className="score-board all">
            All
            <span className="score"> {total_tests} </span>
          </div>
          <div
            className="score-board pass"
            style={{ color: expected > 0 ? "#2fd711" : "inherit" }}
          >
            Passed
            <span className="score"> {expected} </span>
          </div>
          <div
            className="score-board fail"
            style={{ color: unexpected > 0 ? "red" : "inherit" }}
          >
            Failed
            <span className="score"> {unexpected} </span>
          </div>
          <div
            className="score-board flaky"
            style={{ color: flaky > 0 ? "yellow" : "inherit" }}
          >
            Flaky
            <span className="score"> {flaky} </span>
          </div>
          <div
            className="score-board skipped"
            style={{ color: skipped > 0 ? "yellow" : "inherit" }}
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
          <span className="branch">{stats.git_branch}</span>
          <span className="time-stamp">@ {formatted_date_time}</span>
        </div>
      </div>
    </div>
  );
}

export default Card;
