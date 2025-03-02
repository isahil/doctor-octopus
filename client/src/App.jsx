import { useState } from "react"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import NavBar from "./component/navbar/navbar.jsx"
import Cards from "./component/card/cards.jsx"
import FixMe from "./component/fixme/fixme.jsx"
import Footer from "./component/footer/footer.jsx"
import Lab from "./component/lab/lab.jsx"
import XTerm from "./component/xterm/xterm.jsx"

function App() {
  const [showFixMe, setShowFixMe] = useState(true)

  return (
    <Router>
      <div className="app">
        <NavBar />
        <div>
          <Routes>
            <Route path="/" element={<Cards />} />
            <Route
              path="/the-lab"
              element={
                <div className="tech-container">
                  {showFixMe && <FixMe />}
                  <div>
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