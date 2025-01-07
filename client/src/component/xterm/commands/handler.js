import LabSettings from "../../lab/lab.json";
import { interactive_mode } from "./interactive.js";

let interactive_mode_status = false;

export const command_handler = ({
  terminal,
  input,
  setShowFixMe,
  update_options_handler,
  clear_selected_options,
  handle_run_click,
}) => {
  switch (true) {
    case input === "test":
      interactive_mode_status = true; // enable interactive mode
      terminal.write(
        "\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m .......\x1B[0m\r"
      );
      terminal.write(
        "\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m Enter value for each command 'key' below in sequence.\x1B[0m\r"
      );

      LabSettings.forEach((setting) => {
        terminal.write(`\r\n\x1B[1;3;36m key = ${setting.key}\x1B[0m\r`);
        terminal.write(`\r\n\x1B[1;3;32m - ${setting.description}\x1B[0m\r`);
        terminal.write(
          `\r\n\x1B[1;3;37m options = ${JSON.stringify(
            setting.options
          )}\x1B[0m\r`
        );
      });
      terminal.write(
        `\r\n\x1B[1;3;36m ----------------- [ Interactive Mode: ON ] ------------------- \x1B[0m\r\n`
      );

      // start with the first setting in the LabSettings array in interactive mode. the output will be passed to the interactive_mode function next time the user enters
      const current_setting = LabSettings[0];
      const current_key = current_setting.key;
      const current_options = current_setting.options;
      terminal.write(
        `\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m enter a value for [${current_key}]\x1B[0m\r`
      );
      terminal.write(
        `\r\n\x1B[1;3;36m options = ${JSON.stringify(current_options)}\x1B[0m\r`
      );
      break;
    case input === "pwd":
      terminal.write(
        "\r\n\x1B[1;3;32m Doc:\x1B[1;3;36m You are in Doctor Octopus' Home... Directory. \x1B[0m\r"
      );
      break;
    case input === "ls":
      terminal.write("\r\n\x1B[1;3;32m Doc:\x1B[1;3;36m Los Santos? \x1B[0m\r");
      break;
    case input === "cd":
      terminal.write("\r\n\x1B[1;3;32m Doc:\x1B[1;3;36m DVD \x1B[0m\r");
      break;
    case input === "clear":
      terminal.clear();
      break;
    case input === "fixme":
      setShowFixMe(true);
      update_options_handler(0, "qa")
      update_options_handler(1, "loan")
      update_options_handler(2, "fix")
      update_options_handler(3, "client")
      terminal.write(
        "\r\x1B[1;3;32m Doc:\x1B[1;3;37m Starting FixMe App...\x1B[0m\r"
      );
      break;
    case input === "exit":
      interactive_mode_status = false; // disable interactive mode
      terminal.write(
        "\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m exiting Interactive Mode ta ta...\x1B[0m\r"
      );
      terminal.write(
        `\r\n\x1B[1;3;31m  ----------------- [ Interactive Mode: OFF ] ------------------- \x1B[0m\r\n`
      );
      clear_selected_options();
      break;
    default:
      if (interactive_mode_status)
        interactive_mode({
          terminal,
          input,
          update_options_handler,
          handle_run_click,
        });
      else
        terminal.write(
          "\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m I can't help you with that. Type 'test' for help.\x1B[0m\r"
        );
      break;
  }
};
