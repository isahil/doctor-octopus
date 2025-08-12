import { useEffect, useState, useRef } from "react"
import Card from "./card"
import "./cards.css"
import Filters from "./filter"
import config from "../../config.json"
import { to_roman_numeral } from "../../util/helper"
const { day_filter_conf, environment_filter_conf } = config
const { VITE_MAIN_SERVER_HOST, VITE_MAIN_SERVER_PORT } = import.meta.env

const Cards = () => {
  const [cards, setCards] = useState([])
  const [totalCards, setTotalCards] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [filters, setFilters] = useState({ source: "remote", day: 1, environment: "qa" })
  const [alert, setAlert] = useState({ new: false, opening: false, active_clients: 0 })
  const [eventSource, setEventSource] = useState(null)
  const clientCountRef = useRef(null)

  const server_url = `http://${VITE_MAIN_SERVER_HOST}:${VITE_MAIN_SERVER_PORT}`

  const start_notification_stream = () => {
    if (eventSource) {
      console.warn("EventSource already initialized, closing the previous connection.")
      eventSource.close()
    }
    // Generate a client ID using current timestamp + random string. TODO: Use a more robust method for production.
    const client_id = `${Date.now()}-${Math.random().toString(36).substring(2, 10)}`
    const event_source = new EventSource(`${server_url}/notifications/${client_id}`)
    setEventSource(event_source)

    event_source.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === "s3") {
        setAlert((prev) => ({ ...prev, new: true }))
      } else if (data.type === "client") {
        const active = data?.active ?? 0
        const max = data?.max ?? null
        const lifetime = data?.lifetime ?? null
        const timestamp = data?.timestamp ?? null
        console.log(`Active clients: ${active} | max : ${max} | lifetime: ${lifetime} | timestamp: ${timestamp}`)
        setAlert((prev) => ({ ...prev, active_clients: active }))
      }
    }

    event_source.onerror = (error) => {
      console.error("SSE connection error:", error)
      event_source.close()

      setTimeout(() => {
        // Browser will automatically attempt to reconnect after a delay.
      }, 5000)
    }
    return event_source
  }

  /**
   * Fetch cards data from the REST API endpoint.
   * Clear the existing states before fetching new cards data.
   * @returns {Promise<void>}
   */
  const get_cards_from_api = async () => {
    setIsLoading(true)
    setCards([])
    setTotalCards(0)
    setAlert((prev) => ({ ...prev, new: false, opening: false })) // clear new cards alert

    const { source, day, environment } = filters
    const url = `${server_url}/cards/?source=${source}&day=${day}&environment=${environment}`
    const request = await fetch(url)
    const response = await request.json()
    if (!request.ok) {
      console.error("Error fetching cards data:", response.error)
      return
    }
    setIsLoading(false)
    setCards(response.cards)
    setTotalCards(response.cards.length)
  }

  useEffect(() => {
    get_cards_from_api()
    const new_event_source = start_notification_stream()

    return () => {
      new_event_source.close()
    }
  }, [filters])

  useEffect(() => {
    // Only run this effect when client_count changes, not on first render
    if (clientCountRef.current) {
      clientCountRef.current.classList.add("pulse")
      setTimeout(() => {
        if (clientCountRef.current) {
          clientCountRef.current.classList.remove("pulse")
        }
      }, 500)
    }
  }, [alert.active_clients])

  if (isLoading) {
    return (
      <div className="loading-screen">
        {/* <p>Loading...</p> */}
        <div className="batman"></div>
      </div>
    )
  }

  return (
    <div className="cards-component">
      <div className="cards-header">
        <div>
          <img
            src="/img/refresh.png"
            alt="refresh"
            className="refresh-button"
            onClick={get_cards_from_api}
          />
        </div>
        <div className="filter-wrapper">
          {filters.source != "local" && (
            <div className="env-filters-wrapper">
              <Filters
                filter_conf={environment_filter_conf}
                filter={filters}
                setFilter={setFilters}
              />
              <span className="filter-label">ENV</span>
            </div>
          )}
          <div className="day-filters-wrapper">
            <Filters filter_conf={day_filter_conf} filter={filters} setFilter={setFilters} />
            <span className="filter-label">{filters["day"] == 1 ? "day" : "days"}</span>
          </div>
        </div>

        <div className="total">{totalCards} cards</div>
        {alert["new"] && <div className="new-pulse"></div>}
        {alert["opening"] && <div className="opening-bars"></div>}
      </div>
      <div className="cards-body">
        {cards.length > 0 ? (
          cards.map((card, index) => (
            <Card key={index} card={card} index={index} filter={filters} setAlert={setAlert} />
          ))
        ) : (
          <p style={{ color: "white", marginTop: "30px" }}>No cards yet</p>
        )}
      </div>
      {/* Roman numeral of active clients count display */}
      {alert.active_clients > 0 && (
        <div className="client-count-roman" ref={clientCountRef}>
          {to_roman_numeral(alert.active_clients)}
        </div>
      )}
    </div>
  )
}

export default Cards
