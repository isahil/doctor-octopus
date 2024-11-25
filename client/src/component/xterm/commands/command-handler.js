import { socket_client } from "../../../util/socket-client.js";
import { reports } from "./reports.js";
import { logs } from "./logs.js";

const handleCommand = async (input, terminal, setShowFixMe) => {
  const test_suites = ["api", "fix", "perf", "ui", "ws"];

  switch (true) {
    case input === "test":
      terminal.write(
        "\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m I can help you with the following commands:"
      );
      test_suites.forEach((suite) => {
        terminal.write(`\r\n\x1B[1;3;37m  - ${suite}\x1B[0m\r`);
      });
      break;
    case input === "ls":
      terminal.write(
        "\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m You can see the following directories:\r\n 1. reports\r\n 2. logs\x1B[0m\r\n"
      );
      break;
    case input === "reports":
      await reports(input, terminal);
      break;
    case input === "logs":
      await logs(input, terminal);
      break;
    case input === "pwd":
      terminal.write(
        "\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m You are in the root directory.\x1B[0m\r"
      );
      break;
    case input === "clear":
      terminal.clear();
      break;
    case input === "fixme":
      setShowFixMe(true);
      terminal.write("\r\x1B[1;3;32m Doc:\x1B[1;3;37m Starting FixMe App...\x1B[0m\r");
      break;
    case test_suites.includes(input):
      terminal.write(
        `\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m Requesting ${input} Tests... \x1B[0m\r`
      );
      await socket_client("suite", input, terminal); // Call the WebSocket server to trigger the test suite
      break;
    default:
      terminal.write(
        "\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m I can't help you with that.\x1B[0m\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m Choose one from below.\x1B[0m\r"
      );
      terminal.write(`\r\n\x1B[1;3;30m      ${test_suites}\x1B[0m\r`);
      break;
  }
};

export default handleCommand;
