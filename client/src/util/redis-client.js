import { createClient } from "redis"
import config from "../config"

const { REDIS_HOST, REDIS_PORT } = config

const client = createClient({
  url: `redis://${REDIS_HOST}:${REDIS_PORT}`, // Update this URL to your Redis server URL if different
})

class Redis {
  constructor() {
    this.connect()
    this.client = client
  }

  async connect() {
    await client.connect()
  }

  async disconnect() {
    await client.quit()
  }

  async hl_push(key, field, data) {
    const response = await client.hGet(key, field)
    if (response) {
      const existing_list = JSON.parse(response)
      existing_list.push(data)
      return await client.hSet(key, field, JSON.stringify(existing_list))
    } else return await client.hSet(key, field, JSON.stringify([data]))
  }

  async hl_pop(key, field) {
    const response = await client.hGet(key, field)
    if (response) {
      const existing_list = JSON.parse(response)
      existing_list.pop()
      return await client.hSet(key, field, JSON.stringify(existing_list))
    } else return null
  }

  async hl_shift(key, field) {
    const response = await client.hGet(key, field)
    if (response) {
      const existing_list = JSON.parse(response)
      existing_list.shift()
      return await client.hSet(key, field, JSON.stringify(existing_list))
    } else return null
  }

  async hl_unshift(key, field, data) {
    const response = await client.hGet(key, field)
    if (response) {
      const existing_list = JSON.parse(response)
      existing_list.unshift(data)
      return await client.hSet(key, field, JSON.stringify(existing_list))
    } else return await client.hSet(key, field, JSON.stringify([data]))
  }
}

export default Redis
