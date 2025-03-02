import { useContext } from 'react'
import { SocketIOContext } from '../context'

export const useSocketIO = () => {
    return useContext(SocketIOContext)
  }