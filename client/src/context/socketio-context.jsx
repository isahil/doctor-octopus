import { io } from "socket.io-client"
import { createContext, useEffect, useState } from "react"

export const SocketIOContext = createContext()

const SocketIOProvider = ({ children, host, port }) => {
  const [sio, setSio] = useState(null)

  useEffect(() => {
    // Establish a WebSocket connection to the server w. the specified host and port on component mount
    const socket = io(`http://${host}:${port}`, {
      path: "/ws/socket.io",
      transports: ["websocket", "polling", "flashsocket"],
    })

    setSio(socket)

    socket.on("connect", () => console.log("Connected to the W.Socket server..."))

    socket.on("disconnect", () => console.log("Disconnected from the W.Socket server..."))

    socket.on("error", (error) => console.log("W.Socket server error: ", error))

    return () => socket.disconnect() // Disconnect the WebSocket connection when the component unmounts
  }, [])

  return <SocketIOContext value={{ sio }}>{children}</SocketIOContext>
}

export default SocketIOProvider
