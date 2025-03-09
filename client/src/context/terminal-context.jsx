import { createContext, useState } from "react"

export const TerminalContext = createContext()

const TerminalProvider = ({ children }) => {
  const [terminal, setTerminal] = useState(null)

  return <TerminalContext value={{ terminal, setTerminal }}>{children}</TerminalContext>
}

export default TerminalProvider
