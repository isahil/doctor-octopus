import { useEffect } from "react"
import "./lab.css"
import config from "../../config.json"
import { useLabOptions, useOptionsUpdate, useSocketIO, useTerminal } from "../../hooks"

const Lab = () => {
  const { sio } = useSocketIO()
  const { terminal } = useTerminal()
  const { selectedOptions } = useLabOptions() // LabOptionsContext that store the selected options state
  const { update_options_handler, handle_run_click } = useOptionsUpdate() // HandleOptionClickContext that store the function to handle the dd option click

  const lab_filters = config["lab_filters"]
  const last_cards_index = lab_filters.length - 1 // index of the last card is used to enable the "Run" button
  const run_button_enabled = selectedOptions[2] !== "fix" && selectedOptions[last_cards_index] // enable the run button if the last card has been selected
  const side = selectedOptions[2]
  const suite = selectedOptions[3]

  if (side === "client" && suite) {
    terminal.write(`\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m FIXME client Heart Beats interval 30s \r\n`)

    // if the selected option is "fix" and the last card has been selected, then enable the websocket listener for the respective fixme session.
    sio.off("fixme") // Remove existing listener to avoid duplicate
    sio.on("fixme", (data) => {
      terminal.write(`\r\n\x1B[1;3;33m server:\x1B[1;3;37m ${JSON.stringify(data)} \r\n`)
    })
  }

  useEffect(() => {
    if (!sio) {
      console.warn("Socket connection not initialized yet...")
      return
    }
  }, [sio])

  return (
    <div className={"lab component enabled"}>
      <div className="lab-title">THE LAB</div>
      <div className="lab-header">
        {Object.entries(selectedOptions).map((entry, i) => {
          // header displaying the selected options
          return <h1 key={i}>{entry[1]}</h1>
        })}
      </div>

      <div className="lab-cards">
        {lab_filters.map((filter, i) => {
          // iterate through the lab cards and render them with dropdown options
          const { name, dependant } = filter
          const prev_option = selectedOptions[i - 1]
          let new_options = []

          if (dependant) {
            // if the new option is "dependant", then the options returned for it are based on the previous selected option.
            new_options = filter.options[prev_option]
          } else new_options = filter.options

          const enabled = i === 0 || prev_option // enable the card if it's the 1st on or if the previous card has been selected
          const selected = selectedOptions[i] // check if the card has been selected

          return (
            <div
              key={i}
              className={`button lab-card-button ${
                enabled ? "enabled" : "disabled" // enable the card if the previous card has been selected
              } ${selected ? "selected" : "not-selected"}`} // check if the card has been selected
            >
              <h2>{name}</h2>
              {enabled && (
                <div className="option-content">
                  {new_options.map((option, j) => {
                    return (
                      <div
                        key={j}
                        className="option-name"
                        onClick={() => update_options_handler(i, option, terminal)}
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
          onClick={() => handle_run_click({ terminal })}
        >
          Run
        </button>
      </div>
    </div>
  )
}

export default Lab
