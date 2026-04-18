import { io } from "socket.io-client"
import { createContext, useEffect, useState } from "react"

export const SocketIOContext = createContext()

const SocketIOProvider = ({ children, host, port, enabled = true }) => {
  const [sio, setSio] = useState(null)

  useEffect(() => {
    if (!enabled) {
      console.log("Socket.IO is disabled.")
      return
    }
    // Establish a WebSocket connection to the server w. the specified host and port on component mount
    const socket = io(`http://${host}:${port}`, {
      path: "/ws/socket.io",
      transports: ["websocket", "polling", "flashsocket"],
      reconnection: false,
      forceNew: true,
      closeOnBeforeunload: true,
    })

    setSio(socket)

    socket.on("connect", () => console.log("Connected to the W.Socket server..."))

    socket.on("disconnect", () => {
      console.log("Disconnected from the W.Socket server...")
      socket.close()
    })

    socket.on("error", (error) => console.log("W.Socket server error: ", error))

    return () => {
      if (socket) {
        socket.removeAllListeners()
        socket.close()
        setSio(null)
      }
    }
  }, [host, port, enabled])
  return <SocketIOContext value={{ sio }}>{children}</SocketIOContext>
}

export default SocketIOProvider
