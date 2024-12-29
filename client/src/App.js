import { useState } from "react";
import Cards from "./component/card/cards";
import XTerm from "./component/xterm/xterm";
import FixMe from "./component/fixme/fixme";
import Lab from "./component/lab/lab.jsx";
import Footer from "./component/footer/footer.jsx";

function App() {
  const [source, set_source] = useState("remote");
  const [showFixMe, setShowFixMe ] = useState(false);

  const toggle_source = () => {
    set_source((current_source) => {
      const updated_source = current_source === "remote" ? "local" : "remote";
      console.log(`Toggle source: ${updated_source}`);
      return updated_source;
    });
  };

  return (
    <div className="app">
      <div className="app-header">
        <div className="source">
        <p className="source-header">{source}</p>
          <label>
            <input type="checkbox" onClick={toggle_source} />
          </label>
          {/* <p className="source-label">source</p> */}
        </div>
        <div className="title">
          <h1>Doctor Octopus</h1>
        </div>
      </div>

      <div className="app-grid">
        <div className="cards-container">
          <Cards source={source} />
        </div>
        <div className="tech-container">
          <XTerm setShowFixMe={setShowFixMe} />
          <Lab />
          {/* showFixMe && <FixMe /> */}{" "}
          {/* Display the FixMe component when showFixMe is true */}
          <FixMe />
        </div>
      </div>
      <div className="app-footer">
        <Footer />
      </div>
    </div>
  );
}

export default App;
