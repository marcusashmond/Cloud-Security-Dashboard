import { io, Socket } from 'socket.io-client'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

let socket: Socket | null = null

export const initializeWebSocket = (clientId: string) => {
  if (socket) {
    return socket
  }

  socket = io(WS_URL, {
    transports: ['websocket'],
    path: `/ws/${clientId}`,
  })

  socket.on('connect', () => {
    console.log('WebSocket connected')
  })

  socket.on('disconnect', () => {
    console.log('WebSocket disconnected')
  })

  return socket
}

export const getSocket = () => socket

export const closeWebSocket = () => {
  if (socket) {
    socket.close()
    socket = null
  }
}
