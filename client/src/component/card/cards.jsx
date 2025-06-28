import { useEffect, useState } from "react"
import Card from "./card"
import "./cards.css"
import Filters from "./filter"
import config from "../../config.json"
const { day_filter_conf, environment_filter_conf } = config
const { VITE_SERVER_HOST, VITE_SERVER_PORT } = import.meta.env

const Cards = () => {
  const [cards, setCards] = useState([])
  const [totalCards, setTotalCards] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [filters, setFilters] = useState({ source: "remote", day: 1, environment: "qa" })
  const [alert, setAlert] = useState({ new: false, opening: false })
  const server_url = `http://${VITE_SERVER_HOST}:${VITE_SERVER_PORT}`

  const toggle_source = () => {
    setFilters((current_filter) => {
      const current_source = current_filter.source
      const updated_source = current_source === "remote" ? "local" : "remote"
      console.log(`Toggled source: ${updated_source}`)
      return { ...current_filter, source: updated_source }
    })
  }

  const start_notification_stream = () => {
    // Generate a client ID using current timestamp + random string. TODO: Use a more robust method for production.
    const client_id = `${Date.now()}-${Math.random().toString(36).substring(2, 10)}`
    const event_source = new EventSource(`${server_url}/notifications/${client_id}`)

    event_source.onmessage = (event) => {
      const data = JSON.parse(event.data)
      // console.log("SSE notification received:", data)
      if (data.type === "new_s3_objects") {
        console.log(`New S3 objects alert: current ${data.count} (prev ${data.previous})`)
        setAlert({ new: true, opening: false })
        // get_cards_from_api() // Refresh Cards
      }
    }
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
    setAlert({ new: false, opening: false })

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
    start_notification_stream()
  }, [filters]) // fetch cards data when the source changes

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
        <div className="source">
          <span className="source-header">{filters["source"]}</span>
          <label>
            <input type="checkbox" onClick={toggle_source} />
          </label>
        </div>
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
    </div>
  )
}

export default Cards
