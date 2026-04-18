import { Routes, Route, useLocation } from "react-router-dom"
import { useEffect, useState } from "react"
import NavBar from "./components/navbar/navbar.jsx"
import Cards from "./components/card/cards.jsx"
import FixMe from "./components/fixme/fixme.jsx"
import LabProvider from "./contexts/lab-context.jsx"
import SocketIOProvider from "./contexts/socketio-context.jsx"
import TerminalProvider from "./contexts/terminal-context.jsx"
import Footer from "./components/footer/footer.jsx"
import Lab from "./components/lab/lab.jsx"
import XTerm from "./components/xterm/xterm.jsx"
import { runtime_config } from "./utils/env_loader.js"

export const { fixme_server_host, fixme_server_port } = runtime_config

function App() {
  const location = useLocation()
  const [isLabRoute, setIsLabRoute] = useState(false)

  useEffect(() => {
    setIsLabRoute(location.pathname === "/the-lab")
  }, [location])

  return (
    <div className="app">
      <NavBar />
      <div>
        <Routes>
          <Route path="/" element={<Cards />} />
          <Route
            path="/the-lab"
            element={
              <SocketIOProvider
                host={fixme_server_host}
                port={fixme_server_port}
                enabled={isLabRoute} // Only enable when on Lab route
              >
                <TerminalProvider>
                  <LabProvider>
                    <div className="tech-container">
                      <FixMe />
                      <div>
                        <XTerm />
                        <Lab />
                      </div>
                    </div>
                  </LabProvider>
                </TerminalProvider>
              </SocketIOProvider>
            }
          />
        </Routes>
      </div>
      <Footer />
    </div>
  )
}

export default App
