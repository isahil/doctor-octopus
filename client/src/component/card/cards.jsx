import React, { useEffect, useState } from "react"
import Card from "./card"
import "./cards.css"
import config from "../../config.json"
import { useSocketIO } from "../../util/socketio-context"
const { CARDS_DAY_FILTERS } = config

const Cards = () => {
  const { sio } = useSocketIO()
  const [cards, setCards] = useState([])
  const [totalCards, setTotalCards] = useState(0)
  const [filter, setFilter] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [source, setSource] = useState("local")
  
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

      sio.emit("cards", { source, filter })
    } catch (error) {
      console.error("Error fetching cards data:", error)
    } finally {
      if (totalCards > 0) setIsLoading(false) // set loading to false after the fetch request completes
    }
  }

  const handle_filter_change = (e) => {
    const value = e.target.value
    console.log("Clicked cards filter: ", e.target.value)
    setFilter(value)
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
        <div className="option-wrapper">
          {CARDS_DAY_FILTERS.map((day, i) => {
            return (
              <label key={i} className={`day-option`}>
                <input
                  key={i}
                  type="radio"
                  name={`day-${day}`}
                  value={day}
                  onChange={handle_filter_change}
                  checked={filter == day}
                ></input>
                <span className={`filter day-${day}`}>{day}</span>
                <span className="filter text">{day === 1 ? "day" : "days"}</span>
              </label>
            )
          })}
        </div>
        <div className="total">{totalCards} cards</div>
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
