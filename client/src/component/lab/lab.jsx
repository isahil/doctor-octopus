import "./lab.css"
import lab_cards from "./lab.json"
import { useLabOptions, useOptionsUpdate } from "./lab-context"
import { useSocketIO } from "../../util/socketio-context"
import { useTerminal } from "../xterm/terminal-context"

const Lab = () => {
  const { sio } = useSocketIO()
  const { terminal } = useTerminal()
  const { selectedOptions } = useLabOptions() // LabOptionsContext that store the selected options state
  const { update_options_handler, handle_run_click } = useOptionsUpdate() // HandleOptionClickContext that store the function to handle the dd option click

  const last_cards_index = lab_cards.length - 1 // index of the last card is used to enable the "Run" button
  const run_button_enabled = selectedOptions[2] !== "fix" && selectedOptions[last_cards_index] // enable the run button if the last card has been selected
  const proto = selectedOptions[2]
  const suite = selectedOptions[3]

  if (proto === "fix" && suite) {
    // if the selected option is "fix" and the last card has been selected, then enable the websocket listener for the respective fixme session.
    sio.off("fixme") // Remove existing listener to avoid duplicate
    sio.on("fixme", (data) => {
      terminal.write(`\r\n\x1B[1;3;33m Server:\x1B[1;3;36m ${JSON.stringify(data)} \r\n`)
    })
  }

  return (
    <div
      className={`lab component ${
        run_button_enabled ? "enabled" : "disabled" // enable the run button if the last card has been selected
      }`}
    >
      <div className="lab-title">THE LAB</div>
      <div className="lab-header">
        {Object.entries(selectedOptions).map((entry, i) => {
          // header displaying the selected options
          return <h1 key={i}>{entry[1]}</h1>
        })}
      </div>

      <div className="lab-cards">
        {lab_cards.map((card, i) => {
          // iterate through the lab cards and render them with dropdown options
          const card_name = card.key
          let card_options

          if (card_name === "suite") {
            // if the card is "suite", then the options are based on the previous selected option. "api", "ui", "fix" have different suite options
            card_options = selectedOptions[i - 1]
              ? card["options"][selectedOptions[i - 1]]
              : card.options
          } else card_options = card.options

          const enabled = i === 0 || selectedOptions[i - 1] // enable the card if the previous card has been selected
          const selected = selectedOptions[i] // check if the card has been selected

          return (
            <div
              key={i}
              className={`button lab-card-button ${
                enabled ? "enabled" : "disabled" // enable the card if the previous card has been selected
              } ${selected ? "selected" : "not-selected"}`} // check if the card has been selected
            >
              <h2>{card_name}</h2>
              {enabled && (
                <div className="option-content">
                  {card_options.map((option, j) => {
                    return (
                      <div
                        key={j}
                        className="option-name"
                        onClick={() => update_options_handler(i, option)}
                      >
                        {option}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
      <div>
        <button
          className={`button run-button ${
            run_button_enabled ? "enabled" : "disabled" // enable the run button if the last card has been selected
          }`}
          onClick={() => handle_run_click()}
        >
          Run
        </button>
      </div>
    </div>
  )
}

export default Lab
