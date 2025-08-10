// This is the entry point of the application
import ReactDOM from "react-dom/client"
import App from "./App.jsx"
import "./App.css"
import { BrowserRouter } from "react-router-dom"

const root = ReactDOM.createRoot(document.getElementById("root"))

root.render(
  // <React.StrictMode> // This is causing the terminal to render twice
  <div className="body">
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </div>
  // </React.StrictMode>
)
