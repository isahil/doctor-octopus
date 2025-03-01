import { useState } from "react"
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom"
import NavBar from "./component/navbar/navbar.jsx"
import Cards from "./component/card/cards.jsx"
import FixMe from "./component/fixme/fixme.jsx"
import Footer from "./component/footer/footer.jsx"
import Header from "./component/header/header.jsx"
import Lab from "./component/lab/lab.jsx"
import XTerm from "./component/xterm/xterm.jsx"

function App() {
  const [source, setSource] = useState("local")
  const [showFixMe, setShowFixMe] = useState(true)

  const toggle_source = () => {
    setSource((current_source) => {
      const updated_source = current_source === "remote" ? "local" : "remote"
      console.log(`Toggled source: ${updated_source}`)
      return updated_source
    })
  }

  return (
    <Router>
      <div className="app">
        <Header source={source} toggle_source={toggle_source} />
        <NavBar />
        <div className="app-grid">
          <Routes>
            <Route path="/" element={<Cards source={source} />} />
            <Route
              path="/the-lab"
              element={
                <div className="tech-container">
                  {showFixMe && <FixMe />}
                  <div className="xterm-lab">
                    <XTerm setShowFixMe={setShowFixMe} />
                    <Lab />
                  </div>
                </div>
              }
            />
          </Routes>
        </div>
        <div className="app-footer">
          <Footer />
        </div>
      </div>
    </Router>
  )
}

export default App
