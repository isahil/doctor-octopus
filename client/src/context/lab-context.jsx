import { createContext, useState } from "react"
import { useTerminal, useSocketIO } from "../hooks"

export const LabOptionsContext = createContext()
export const OptionsUpdateContext = createContext()

/**
 * LabProvider component/context to handle and share the state of the selected lab options
 * @param {*} param0 object that contains the children components
 * @returns
 */
const LabProvider = ({ children }) => {
  const { sio } = useSocketIO()
  const { terminal } = useTerminal()
  const [selectedOptions, setSelectedOptions] = useState({}) // store the selected options

  const update_options_handler = (option_index, option_value) => {
    // update the option selected for the card so the next card can be enabled
    console.log(`Lab card #${option_index}: ${option_value}`)
    setSelectedOptions((prev_options) => {
      let updated_options = {},
        index = 0 // update/reset the selected options upto the current card index
      while (index < option_index) {
        updated_options[index] = prev_options[index]
        index++
      }
      updated_options[option_index] = option_value
      return updated_options
    })

    if (selectedOptions[2] === "fix" && selectedOptions[3]) {
      console.log("FixMe enabled")
      sio.off("fixme") // Remove existing listener to avoid duplicate
      sio.on("fixme", (data) => {
        terminal.write(`\r\n\x1B[1;3;33m server:\x1B[1;3;37m ${JSON.stringify(data)} \r\n`)
      })
    }
  }

  const clear_selected_options = () => {
    setSelectedOptions({})
  }

  const handle_run_click = ({ terminal: interactive_terminal, interactive_selectedOptions }) => {
    // interactive mode will pass the terminal and selectedOptions as a parameter
    const _terminal = interactive_terminal ?? terminal
    const _selectedOptions = interactive_selectedOptions ?? selectedOptions

    const subscription = "the-lab" // listen for the-lab-log events from the server
    sio.off(subscription) // Remove existing listener to avoid duplicate logs
    sio.on(subscription, (line) => {
      _terminal.write(`\r ${line}\r`)
    })

    // data to send in the request query
    const environment = _selectedOptions[0]
    const app = _selectedOptions[1]
    const proto = _selectedOptions[2]
    const suite = _selectedOptions[3]
    const command = { environment, app, proto, suite }

    _terminal.write(
      `\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m Running command ⫷⫷⫷⫷⫷  ${JSON.stringify(command)}  ⫸⫸⫸⫸⫸\r\n`
    )
    // terminal.write(`▁▁▂▃▄▅▆▇█ \n`)
    clear_selected_options()
    sio.emit(subscription, command)
    _terminal.write(`\r\n\x1B[1;3;31m You\x1B[0m $ `)
  }

  return (
    <LabOptionsContext value={{ selectedOptions }}>
      <OptionsUpdateContext
        value={{
          update_options_handler,
          clear_selected_options,
          handle_run_click,
        }}
      >
        {children}
      </OptionsUpdateContext>
    </LabOptionsContext>
  )
}

export default LabProvider
