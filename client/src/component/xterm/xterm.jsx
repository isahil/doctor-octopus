import { useEffect, useRef } from "react"
import { Terminal } from "@xterm/xterm"
import { FitAddon } from "@xterm/addon-fit"
import "./xterm.css"
import { useOptionsUpdate, useSocketIO, useTerminal } from "../../hooks"
import { command_handler } from "./commands/handler.js"

const XTerm = ({ setShowFixMe }) => {
  const terminalRef = useRef(null)
  const { update_options_handler, clear_selected_options, handle_run_click } = useOptionsUpdate() // HandleOptionClickContext that store the function to handle the dd option click
  const { terminal, setTerminal } = useTerminal() // TerminalContext that store the terminal object
  const { sio } = useSocketIO()

  const xterm = (terminal) => {
    if (!terminal) return
    terminal.options.theme.foreground = "cyan"
    terminal.options.cursorStyle = "underline"
    terminal.options.cursorBlink = true

    const fitAddon = new FitAddon() // FitAddon to fit the terminal to the container
    if (terminal) terminal.loadAddon(fitAddon)
    terminal.open(terminalRef.current)
    fitAddon.fit()

    terminal.write(
      "\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m Hi, I'm\x1B[1;3;32m Doctor Octopus\x1B[1;3;37m. Type 'sdet' to start the Interactive Mode.\x1B[0m\r\n"
    )
    terminal.write(`\x1B[1;3;31m You\x1B[0m $ `)

    let input = "",
      cursor = 0
    terminal.onData((data) => {
      const ascii_code = data.charCodeAt(0)
      // console.log(`input ASCII code: ${ascii_code}`);
      switch (ascii_code) {
        case 27:
          const key = data.substring(1)
          if (key === "[C") {
            // Right // console.log(`-> ${JSON.stringify(data.substring(1))}`);
            if (cursor < input.length) {
              terminal.write(data)
              cursor++
            }
          } else if (key === "[D") {
            // Left // console.log(`<- ${JSON.stringify(data.substring(1))}`);
            if (cursor > 0) {
              cursor--
              terminal.write(data)
            }
          }
          break
        case 13:
          // Enter
          command_handler({
            terminal,
            input,
            setShowFixMe,
            update_options_handler,
            clear_selected_options,
            handle_run_click,
          })
          terminal.write(`\r\n\x1B[1;3;31m You\x1B[0m $ `)
          input = ""
          cursor = 0
          break
        case ascii_code < 32 || ascii_code === 127:
          // Control characters
          break
        case 127:
          // Backspace
          if (cursor > 0) {
            input = input.substring(0, cursor - 1) + input.substring(cursor)
            cursor--
            terminal.write("\b" + input.substring(cursor) + " \b")
          }
          break
        default:
          // Visible characters
          input = input.substring(0, cursor) + data + input.substring(cursor)
          cursor++
          terminal.write(data)
          break
      }
    })
  }

  useEffect(() => {
    if (terminalRef.current && sio) {
      const terminal = new Terminal()
      setTerminal(terminal)
      const fitAddon = new FitAddon()
      terminal.loadAddon(fitAddon)
      fitAddon.fit()
      xterm(terminal)
    }

    return () => {
      if (terminal) {
        terminal.dispose()
      }
    }
  }, [sio, terminalRef])

  return <div ref={terminalRef} id="terminal" className="xterm component"></div>
}

export default XTerm
