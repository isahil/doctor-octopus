// This is the entry point of the application
import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App.jsx"
import "./App.css"
import config from "./config"
import LabProvider from "./component/lab/lab-context.jsx"
import SocketIOProvider from "./util/socketio-context.jsx"
import TerminalProvider from "./component/xterm/terminal-context.jsx"

export const { SERVER_HOST, SERVER_PORT } = config
console.log(`Server host: ${SERVER_HOST} | Server port: ${SERVER_PORT}`)

const root = ReactDOM.createRoot(document.getElementById("root"))

root.render(
  // <React.StrictMode> // This is causing the terminal to render twice
  <>
    <div className="body">
      <SocketIOProvider host={SERVER_HOST} port={SERVER_PORT}>
        <TerminalProvider>
          <LabProvider>
            <App />
          </LabProvider>
        </TerminalProvider>
      </SocketIOProvider>
    </div>
  </>
  // </React.StrictMode>
)
