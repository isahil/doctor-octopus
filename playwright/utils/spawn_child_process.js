import { spawn } from "child_process"

/**
 * execute a shell command in a sub-shell
 * @param command for shell to execute
 * @param callback function to execute on process.exit. callback is responsible for exit if passed
 */
export const spawn_child_process = (command, callback) => {
  console.info(`Executing command: '${command}'`)
  spawn(command, { shell: true, stdio: "inherit" })
    .on("close", (code) => {
      console.info(`Script execution closed with code: ${code}`)
      callback ? callback(code) : process.exit(code ?? 1)
    })
    .on("error", (err) => {
      logger.error(`Script execution error: ${JSON.stringify(err)}`)
      process.exit(1)
    })
    .on("exit", (code) => {
      console.info(`Script execution exited with code: ${code}`)
      if (!callback) process.exit(code ?? 1)
    })
    .on("disconnect", () => {
      console.info("Script execution disconnected")
      process.exit(1)
    })
    .on("message", (message) => {
      console.info(`Script execution message: ${JSON.stringify(message)}`)
      process.exit(1)
    })
}
