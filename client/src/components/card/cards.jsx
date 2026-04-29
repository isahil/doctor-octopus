import { useEffect, useState, useRef } from "react"
import Card from "./card"
import "./cards.css"
import Filters from "./filter"
import config from "../../config.json"
import { to_roman_numeral } from "../../utils/helper"
import { runtime_config } from "../../utils/env_loader"

const Cards = () => {
  const { main_api_base_url } = runtime_config
  const { card_filters } = config

  const initial_filter_state = (() => {
    const default_filter_state = card_filters.reduce((def_state, filter) => {
      const { name, default: default_val } = filter
      console.log(`default value for ${name} -> ${default_val}`)
      def_state[name] = default_val
      return def_state
    }, {})
    console.log(`def_obj: ${JSON.stringify(default_filter_state)}`)
    return default_filter_state
  })()

  const [cards, setCards] = useState([])
  const [totalCards, setTotalCards] = useState(0)
  const [cardsQueued, setCardsQueued] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [cardFilters, setCardFilters] = useState(initial_filter_state)
  const [filterConfigs, setFilterConfigs] = useState(card_filters)
  const [alert, setAlert] = useState({ new: false, opening: false, active_clients: 0 })
  const [eventSource, setEventSource] = useState(null)
  const clientCountRef = useRef(null)

  const start_notification_stream = () => {
    if (eventSource) {
      console.warn("EventSource already initialized, closing the previous connection.")
      eventSource.close()
    }
    // Generate a client ID using current timestamp + random string. TODO: Use a more robust method for production.
    const client_id = `${Date.now()}-${Math.random().toString(36).substring(2, 10)}`
    const event_source = new EventSource(`${main_api_base_url}/notifications/${client_id}`)
    setEventSource(event_source)

    event_source.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === "download") {
        setAlert((prev) => ({ ...prev, new: true }))
        const card_date = data?.card_date
        setCardsQueued((prev) => prev.filter((date) => date !== card_date)) // remove from queued state to trigger UI update if the card is already rendered
      } else if (data.type === "client") {
        const active = data?.active ?? 0
        const max = data?.max ?? null
        const lifetime = data?.lifetime ?? null
        console.log(
          `Active clients: ${active} | max : ${max} | lifetime: ${lifetime} | timestamp: ${new Date().toLocaleString()}`
        )
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

    const { environment, day, product, protocol } = cardFilters
    const cards_url = `${main_api_base_url}/cards/?mode=cache&day=${day}&environment=${environment}&product=${product}&protocol=${protocol}`
    const cards_queue_url = `${main_api_base_url}/cards-download-queue`
    const cards_request = fetch(cards_url)
    const cards_queue_request = fetch(cards_queue_url)
    const [cards_response, cards_queue_response] = await Promise.all([
      cards_request,
      cards_queue_request,
    ])

    const cards_res_json = await cards_response.json()
    const cards_queue_res_json = await cards_queue_response.json()
    if (!cards_response.ok) {
      console.error("Error fetching cards data:", cards_res_json.error)
      return
    }

    const sdets_set = new Set(["all"])
    cards_res_json.cards.forEach((card) => {
      const { json_report } = card
      const uname = json_report?.stats?.username || "unknown"
      sdets_set.add(uname)
    })
    console.log(`SDETS in response: ${JSON.stringify(Array.from(sdets_set))}`)

    setFilterConfigs((prevConfigs) =>
      prevConfigs.map((_filter) =>
        _filter.name === "sdet" ? { ..._filter, options: Array.from(sdets_set) } : _filter
      )
    )

    console.log(`Cards queued for download: ${JSON.stringify(cards_queue_res_json)}`)
    setCardsQueued(cards_queue_res_json.queued || [])
    setIsLoading(false)
    setCards(cards_res_json.cards)
    setTotalCards(cards_res_json.cards.length)
  }

  useEffect(() => {
    get_cards_from_api()
    const new_event_source = start_notification_stream()

    return () => {
      new_event_source.close()
    }
  }, [cardFilters])

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
        <div className="stethoscope-loader" aria-hidden="true">
          <div className="stethoscope-tube"></div>
          <div className="stethoscope-stem"></div>
          <div className="stethoscope-chest"></div>
          <div className="stethoscope-pulse"></div>
        </div>
        <p className="loading-caption">Checking test reports...</p>
      </div>
    )
  }

  return (
    <div className="cards-component">
      <div className="cards-header">
        <div className="cards-header-left">
          <div className="filters-wrapper">
            {filterConfigs.map((filterConfig, index) => {
              return (
                <div key={index} className={`${filterConfig.name}-filters-wrapper`}>
                  <Filters
                    filter={filterConfig}
                    cardFilters={cardFilters}
                    setCardFilters={setCardFilters}
                  />
                  <span className="filter-label">{filterConfig.label}</span>
                </div>
              )
            })}
          </div>
        </div>

        <div className="cards-header-center">
          <span className="total-count">{totalCards}</span>
          <span className="total-label-text">cards</span>
        </div>
        <div className="cards-header-right">
          <div className="refresh-button">
            <img src="/img/refresh.png" alt="refresh" onClick={get_cards_from_api} />
          </div>
          {alert["new"] && <div className="new-pulse"></div>}
          {alert["opening"] && <div className="opening-bars"></div>}
        </div>
      </div>
      <div className="cards-body">
        {cards.length > 0 ? (
          cards.map((card, index) => {
            const { day } = card.filter_data
            return (
              <Card
                key={index}
                card={card}
                index={index}
                filter={cardFilters}
                setAlert={setAlert}
                queued={cardsQueued.includes(day)}
              />
            )
          })
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
