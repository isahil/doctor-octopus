import { useState } from "react"
import Cards from "./component/card/cards.jsx"
import FixMe from "./component/fixme/fixme.jsx"
import Footer from "./component/footer/footer.jsx"
import Header from "./component/header/header.jsx"
import Lab from "./component/lab/lab.jsx"
import XTerm from "./component/xterm/xterm.jsx"

function App() {
  const [source, setSource] = useState("remote")
  const [showFixMe, setShowFixMe] = useState(true)

  const toggle_source = () => {
    setSource((current_source) => {
      const updated_source = current_source === "remote" ? "local" : "remote"
      console.log(`Toggled source: ${updated_source}`)
      return updated_source
    })
  }

  return (
    <div className="app">
      <Header source={source} toggle_source={toggle_source} />
      <div className="app-grid">
        <div className="cards-container">
          <Cards source={source} />
        </div>
        <div className="tech-container">
          <XTerm setShowFixMe={setShowFixMe} />
          <Lab />
          {showFixMe && <FixMe />}
          {/* Display the FixMe component when showFixMe is true */}
          {/* <FixMe /> */}
        </div>
      </div>
      <div className="app-footer">
        <Footer />
      </div>
    </div>
  )
}

export default App
