import { createClient } from "redis"

// const { VITE_REDIS_HOST, VITE_REDIS_PORT } = process.env

export class Redis {
  constructor() {
    this.client = this.connect()
  }

  connect() {
    const client = createClient({
      url: `redis://localhost:6379`, // Update this URL to your Redis server URL if different
    })
    client.connect()
    return client
  }

  async disconnect() {
    await this.client.quit()
  }

  async hl_push(key, field, data) {
    const response = await this.client.hGet(key, field)
    if (response) {
      const existing_list = JSON.parse(response)
      existing_list.push(data)
      return await this.client.hSet(key, field, JSON.stringify(existing_list))
    } else return await this.client.hSet(key, field, JSON.stringify([data]))
  }

  async hl_pop(key, field) {
    const response = await this.client.hGet(key, field)
    if (response) {
      const existing_list = JSON.parse(response)
      existing_list.pop()
      return await this.client.hSet(key, field, JSON.stringify(existing_list))
    } else return null
  }

  async hl_shift(key, field) {
    const response = await this.client.hGet(key, field)
    if (response) {
      const existing_list = JSON.parse(response)
      existing_list.shift()
      return await this.client.hSet(key, field, JSON.stringify(existing_list))
    } else return null
  }

  async hl_unshift(key, field, data) {
    const response = await this.client.hGet(key, field)
    if (response) {
      const existing_list = JSON.parse(response)
      existing_list.unshift(data)
      return await this.client.hSet(key, field, JSON.stringify(existing_list))
    } else return await this.client.hSet(key, field, JSON.stringify([data]))
  }
}
