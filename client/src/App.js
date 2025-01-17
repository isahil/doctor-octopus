import { useState } from "react";
import Cards from "./component/card/cards";
import FixMe from "./component/fixme/fixme";
import Footer from "./component/footer/footer.jsx";
import Header from "./component/header/header.jsx";
import Lab from "./component/lab/lab.jsx";
import XTerm from "./component/xterm/xterm";

function App() {
  const [source, set_source] = useState("local");
  const [showFixMe, setShowFixMe ] = useState(false);

  const toggle_source = () => {
    set_source((current_source) => {
      const updated_source = current_source === "remote" ? "local" : "remote";
      console.log(`Toggled source: ${updated_source}`);
      return updated_source;
    });
  };

  /**
   * I am creating a pull request to fix the issue  #1
   */

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
