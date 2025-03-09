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
  const [source, setSource] = useState("remote")
  const [filter, setFilter] = useState({ day: "1", environment: "qa" })

  const toggle_source = () => {
    setSource((current_source) => {
      const updated_source = current_source === "remote" ? "local" : "remote"
      console.log(`Toggled source: ${updated_source}`)
      return updated_source
    })
  }
  /**
   * fetch cards data from the FASTAPI server. TODO: Implement the WebSocket subscription logic
   */
  const get_cards = async () => {
    setIsLoading(true) // set loading to true before the fetch request starts
    setCards([]) // clear the existing cards
    setTotalCards(0) // clear the existing total cards
    try {
      if (!sio) {
        console.warn("Socket connection not initialized")
        return
      }

      sio.off("cards") // Remove existing listener before adding a new one

      sio.on("cards", (card) => {
        setIsLoading(false)
        if (!card) {
          console.log("No cards found") // log a message if no cards are found
          return setCards([]) // clear the existing cards if no cards are found
        }
        setTotalCards((prevTotalCards) => prevTotalCards + 1)
        if (card.json_report.suites.length <= 0) return // filter out cards that did not run any test suites
        console.log(
          `Total ${source} cards: ${totalCards} | card test_suite: ${card.json_report.stats.test_suite}`
        )
        setCards((prevCards) => [...prevCards, card])
      })

      sio.emit("cards", { source, filter }) // emit a message to the server to fetch cards data
    } catch (error) {
      console.error("Error fetching cards data:", error)
    } finally {
      if (totalCards > 0) setIsLoading(false) // set loading to false after the fetch request completes
    }
  }

  useEffect(() => {
    get_cards()
  }, [sio, source, filter]) // fetch cards data when the source changes

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
          <div className="day-filters-wrapper">
            <Filters filter_conf={day_filter_conf} filter={filter} setFilter={setFilter} />
          </div>
          <div className="env-filters-wrapper">
            <Filters
              filter_conf={environment_filter_conf}
              filter={filter}
              setFilter={setFilter}
            />
          </div>
        </div>

        <div className="total">{totalCards} cards</div>
        <div className="bars"></div>
        <div className="pulse"></div>
        <div className="source">
          <span className="source-header">{source}</span>
          <label>
            <input type="checkbox" onClick={toggle_source} />
          </label>
        </div>
      </div>
      <div className="cards-body">
        {cards.length > 0 ? (
          cards.map((card, index) => <Card key={index} source={source} card={card} index={index} />)
        ) : (
          <p style={{ color: "white", marginTop: "30px" }}>No cards yet</p>
        )}
      </div>
    </div>
  )
}

export default Cards
