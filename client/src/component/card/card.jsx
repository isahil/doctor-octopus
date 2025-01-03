import React from "react";
import "./card.css";
import { SERVER_HOST, SERVER_PORT } from "../../index";
import { useTerminal } from "../xterm/terminal-context";

function Card({ source, card, index }) {
  const { json_report, html_report, root_dir } = card;
  const { stats, suites } = json_report;
  const { terminal } = useTerminal();
  // console.log(`Stats: ${JSON.stringify(stats)} \n${html_report.length === 0 ? "No HTML Report" : "Yes HTML Report"}`);
  const { expected, flaky, skipped, unexpected, startTime } = stats; // scoreboard values to display
  const project_name = suites[0].specs[0] // check if the suite is a spec or a suite. TODO: Need to figure out the logic
    ? suites[0].specs[0].tests[0].projectId
    : suites[0].suites[0].specs[0].tests[0].projectId; // get the project name for the card title
  const total_tests = expected + flaky + unexpected;

  const date = new Date(startTime); // convert startTime to a Date object
  const formatted_date_time = date.toLocaleString(); // adjust formatting as needed

  const handle_view_report_click = async () => {
    console.log(`View report: ${html_report}`);
    const response = await fetch(
      `http://${SERVER_HOST}:${SERVER_PORT}/card?source=${source}&root_dir=${root_dir}`
    );
    const output = await response.text();
    terminal.write(`\r\n\x1B[1;3;33m Server:\x1B[1;3;36m ${JSON.stringify(output)} \r\n`);
    terminal.write(`\x1B[1;3;31m You\x1B[0m $ `);
    // try {
    //   const reportWindow = window.open('http://localhost:9323', '_blank');
    //   if (!reportWindow) {
    //     alert('Popup was blocked. Please allow popups for this website.');
    //   }
    // } catch (error) {
    //   console.error('Error opening report window:', error);
    //   alert('Failed to open report window. Please try again.');
    // }
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
          <span className="branch">{stats.git_branch}</span>
          <span className="time-stamp">@ {formatted_date_time}</span>
        </div>
      </div>
    </div>
  );
}

export default Card;
