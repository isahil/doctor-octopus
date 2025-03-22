import React, { useEffect, useState } from "react"
import Card from "./card"
import "./cards.css"
import { useSocketIO } from "../../hooks"
import Filters from "./filter"
import config from "../../config.json"
const { day_filter_conf, environment_filter_conf } = config

const Cards = () => {
  const { sio } = useSocketIO()
  const [cards, setCards] = useState([])
  const [totalCards, setTotalCards] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [filters, setFilters] = useState({ source: "remote", day: 1, environment: "qa" })
  const [alert, setAlert] = useState({ new: false, opening: false })

  const toggle_source = () => {
    setFilters((current_filter) => {
      const current_source = current_filter.source
      const updated_source = current_source === "remote" ? "local" : "remote"
      console.log(`Toggled source: ${updated_source}`)
      return { ...current_filter, source: updated_source }
    })
  }
  /**
   * fetch cards data from the FASTAPI server. TODO: Implement the WebSocket subscription logic
   */
  const get_cards = async () => {
    // clear the existing states before fetching new cards data
    setIsLoading(true)
    setCards([])
    setTotalCards(0)
    setAlert({ new: false, opening: false })
    try {
      if (!sio) {
        console.warn("Socket connection not initialized yet...")
        return
      }
      sio.off("alert") // Remove existing listeners before adding a new one
      sio.off("cards")

      sio.on("cards", (card) => {
        setIsLoading(false)
        if (!card) {
          console.log("No cards found") // log a message if no cards are found
          return setCards([]) // clear the existing cards if no cards are found
        }
        if (card.json_report.suites.length <= 0) return // filter out cards that did not run any test suites
        setTotalCards((prevTotalCards) => prevTotalCards + 1)
        setCards((prevCards) => [...prevCards, card])
        // console.log(`Total ${filter.source} cards: ${totalCards} | card test_suite: ${card.json_report.stats.test_suite}`)
      })

      sio.emit("cards", filters) // emit a message to the server to fetch cards data

      sio.on("alert", (data) => {
        const { new_alert } = data
        setAlert((prev) => ({ ...prev, new: new_alert }))
      })
    } catch (error) {
      console.error("Error fetching cards data:", error)
    } finally {
      if (totalCards > 0) setIsLoading(false) // set loading to false after the fetch request completes
    }
  }

  useEffect(() => {
    get_cards()
  }, [sio, filters]) // fetch cards data when the source changes

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
            onClick={get_cards}
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
