import { io } from "socket.io-client";
import React, { useEffect, useContext } from "react";
import { SERVER_HOST, SERVER_PORT } from "../index";
const SocketIOContext = React.createContext();

export const useSocketIO = () => {
  return useContext(SocketIOContext);
};

const SocketIOProvider = ({ children }) => {
  const [sio, setSio] = React.useState(null);

  useEffect(() => {
    // Establish a WebSocket connection to your server
    const socket = io(`http://${SERVER_HOST}:${SERVER_PORT}`, {
      path: "/ws/socket.io",
      transports: ["websocket", "polling", "flashsocket"],
    });

    socket.on("connect", () =>
      console.log("Connected to the W.Socket server...")
    );

    socket.on("disconnect", () =>
      console.log("Disconnected from the W.Socket server...")
    );

    socket.on("error", (error) =>
      console.log("W.Socket server error: ", error)
    );

    setSio(socket);

    return (() => socket.disconnect()) 
  }, []);

  return (
    <SocketIOContext.Provider value={{ sio }}>
      { children }
    </SocketIOContext.Provider>
  );
};

export default SocketIOProvider;
