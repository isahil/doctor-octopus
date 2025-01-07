import { useContext, useState } from "react";
import React from "react";
import { useTerminal } from "../xterm/terminal-context";
import { useSocketIO } from "../../util/socketio-context";

const LabOptionsContext = React.createContext();
const OptionsUpdateContext = React.createContext();

/**
 * custom hooks for handling the lab options context/state
 * @returns {Object} context for lab options - selected options
 */
export const useLabOptions = () => {
  return useContext(LabOptionsContext);
};

/**
 * custom hooks for handling the option click context/state
 * @returns {Object} context for handle_option_click - function to handle the dd option click
 */
export const useOptionsUpdate = () => {
  return useContext(OptionsUpdateContext);
};

/**
 * LabProvider component/context to handle and share the state of the selected lab options
 * @param {*} param0 object that contains the children components
 * @returns
 */
const LabProvider = ({ children }) => {
  const [selectedOptions, setSelectedOptions] = useState({}); // store the selected options
  const { terminal } = useTerminal();
  const { sio } = useSocketIO();

  const update_options_handler = (option_index, option_value) => {
    // update the option selected for the card so the next card can be enabled
    console.log(`Lab card #${option_index}: ${option_value}`);
    setSelectedOptions((prev_options) => {
      let updated_options = {},
        index = 0; // update/reset the selected options upto the current card index
      while (index < option_index) {
        updated_options[index] = prev_options[index];
        index++;
      }
      updated_options[option_index] = option_value;
      return updated_options;
    });

    if(selectedOptions[2] === "fix" && selectedOptions[3]) {
      console.log("FixMe selected");
      sio.off("fixme"); // Remove existing listener to avoid duplicate
      sio.on("fixme", (data) => {
        console.log("W.Socket server: ", data);
        terminal.write(`\r\n\x1B[1;3;33m Server: ${data} \r\n`);
      });
    }
  };

  const clear_selected_options = () => {
    setSelectedOptions({});
  };

  const handle_run_click = async (interactive = false) => {
    // listen for the-lab-log events from the server
    const subscription = "the-lab-log"
    sio.off(subscription); // Remove existing listener to avoid duplicate logs
    sio.on(subscription, line => {
      terminal.write(`\r ${line}\r`);
    });

    // data to send in the request query
    const env = selectedOptions[0];
    const app = selectedOptions[1];
    const proto = selectedOptions[2];
    const suite = selectedOptions[3];
    const command = { environment: env, app: app, proto: proto, suite: suite };

    terminal.write(
      `\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m Running command ⫷⫷⫷⫷⫷  ${JSON.stringify(command)}  ⫸⫸⫸⫸⫸\r\n`
    );
    // terminal.write(`▁▁▂▃▄▅▆▇█ \n`)
    clear_selected_options();
    sio.emit("the-lab", command);
    terminal.write(`\r\n\x1B[1;3;31m You\x1B[0m $ `);
  };

  return (
    <LabOptionsContext.Provider value={{ selectedOptions }}>
      <OptionsUpdateContext.Provider
        value={{
          update_options_handler,
          clear_selected_options,
          handle_run_click,
        }}
      >
        {children}
      </OptionsUpdateContext.Provider>
    </LabOptionsContext.Provider>
  );
};

export default LabProvider;
