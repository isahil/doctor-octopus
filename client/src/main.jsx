// This is the entry point of the application
import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App.jsx"
import "./App.css"
import LabProvider from "./context/lab-context.jsx"
import SocketIOProvider from "./context/socketio-context.jsx"
import TerminalProvider from "./context/terminal-context.jsx"

export const { VITE_FIXME_SERVER_HOST, VITE_FIXME_SERVER_PORT } = import.meta.env

const root = ReactDOM.createRoot(document.getElementById("root"))

root.render(
  // <React.StrictMode> // This is causing the terminal to render twice
  <div className="body">
    <SocketIOProvider host={VITE_FIXME_SERVER_HOST} port={VITE_FIXME_SERVER_PORT}>
      <TerminalProvider>
        <LabProvider>
          <App />
        </LabProvider>
      </TerminalProvider>
    </SocketIOProvider>
  </div>
  // </React.StrictMode>
)
