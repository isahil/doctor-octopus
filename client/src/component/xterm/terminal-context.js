import React, { useState, useContext } from "react"

const TerminalContext = React.createContext()

export const useTerminal = () => useContext(TerminalContext)

const TerminalProvider = ({ children }) => {
  const [terminal, setTerminal] = useState(null)

  return (
    <TerminalContext.Provider value={{ terminal, setTerminal }}>
      {children}
    </TerminalContext.Provider>
  )
}

export default TerminalProvider
