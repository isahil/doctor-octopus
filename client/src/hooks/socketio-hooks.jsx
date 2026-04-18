import { useContext } from "react"
import { SocketIOContext } from "../contexts"

export const useSocketIO = () => {
  return useContext(SocketIOContext)
}
