import React, { useState, useContext } from "react"

const TerminalContext = React.createContext()

export const useTerminal = () => useContext(TerminalContext)

const TerminalProvider = ({ children }) => {
  const [terminal, setTerminal] = useState(null)

  return (
    <TerminalContext value={{ terminal, setTerminal }}>
      { children }
    </TerminalContext>
  )
}

export default TerminalProvider
