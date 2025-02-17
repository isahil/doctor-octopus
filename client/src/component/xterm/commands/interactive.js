import LabSettings from "../../lab/lab.json"

let current_option_index = 0,
  selected_option = ""

export const interactive_mode = ({ terminal, input, update_options_handler, handle_run_click }) => {
  const last_cards_index = LabSettings.length // index of the last card is used to enable the "Run" button
  console.log(`xterm - current_option_index: ${current_option_index} - input: ${input}`)

  // TODO: Add the logic to disable the handle_run_click function if the selected_options is ["client", "dealer"]
  // TODO: Add the logic to disable interactiveMode after the "Run" button is clicked
  if (current_option_index === last_cards_index && input === "run") {
    handle_run_click(terminal)
    current_option_index = 0 // reset the current_option_index for the next interactive
    selected_option = ""
    return
  }

  selected_option = input // store the selected option for the current card to verify if the "Run" button should be enabled
  update_options_handler(current_option_index, input) // update the selected option for the currentOptionIndex card
  current_option_index++ // increment the display messages for the next card options

  if (current_option_index === last_cards_index) {
    console.log(`xterm - selected_options: ${JSON.stringify(selected_option)}`)
    let message
    if (["client", "dealer"].includes(selected_option)) {
      message = "\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m all options selected. FixMe app is enabled.\x1B[0m\r"
      current_option_index = 0
      selected_option = ""
    } else
      message = "\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m All options selected. Type 'run' to execute the command.\x1B[0m\r"
    terminal.write(message)
  } else {
    // display the next card options for the user to select
    const current_setting = LabSettings[current_option_index]
    const current_key = current_setting.key
    const current_options = current_setting.options

    terminal.write(`\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m enter a value for [${current_key}]\x1B[0m\r`)
    terminal.write(`\r\n\x1B[1;3;36m options = ${JSON.stringify(current_options)}\x1B[0m\r`)
  }
}
