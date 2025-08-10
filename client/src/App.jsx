import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom"
import { useEffect, useState } from "react"
import NavBar from "./component/navbar/navbar.jsx"
import Cards from "./component/card/cards.jsx"
import FixMe from "./component/fixme/fixme.jsx"
import LabProvider from "./context/lab-context.jsx"
import SocketIOProvider from "./context/socketio-context.jsx"
import TerminalProvider from "./context/terminal-context.jsx"
import Footer from "./component/footer/footer.jsx"
import Lab from "./component/lab/lab.jsx"
import XTerm from "./component/xterm/xterm.jsx"

export const { VITE_FIXME_SERVER_HOST, VITE_FIXME_SERVER_PORT } = import.meta.env

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
                host={VITE_FIXME_SERVER_HOST}
                port={VITE_FIXME_SERVER_PORT}
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
