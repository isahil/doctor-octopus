import React, { useEffect, useState } from "react"
import Card from "./card"
import "./cards.css"
import config from "../../config.json"
const { SERVER_HOST, SERVER_PORT, CARDS_DAY_FILTERS } = config

const Cards = ({ source }) => {
  const [cards, setCards] = React.useState([])
  const [totalCards, setTotalCards] = useState(0)
  const [cardsFilter, setCardsFilter] = useState(1)
  const [isLoading, setIsLoading] = useState(true)

  /**
   * fetch cards data from the FASTAPI server. TODO: Implement the WebSocket subscription logic
   */
  const get_cards = async () => {
    setIsLoading(true) // set loading to true before the fetch request starts
    try {
      const response = await fetch(
        `http://${SERVER_HOST}:${SERVER_PORT}/cards?source=${source}&filter=${cardsFilter}`
      )
      const data = await response.json()
      setTotalCards(data.length)
      const filtered_data = data.filter((card) => card.json_report.suites.length > 0) // filter out cards that did not run any test suites
      console.log(`Total ${source} cards: ${data.length} | filtered cards: ${filtered_data.length}`)
      setCards(filtered_data)
    } catch (error) {
      console.error("Error fetching cards data:", error)
    } finally {
      setIsLoading(false) // set loading to false after the fetch request completes
    }
  }

  const handle_filter_change = (e) => {
    const value = e.target.value
    console.log("Clicked cards filter: ", e.target.value)
    setCardsFilter(value)
  }

  useEffect(() => {
    get_cards()
  }, [source, cardsFilter]) // fetch cards data when the source changes

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
                  checked={cardsFilter == day}
                ></input>
                <span className={`filter day-${day}`}>{day}</span>
                <span className="filter text">{day === 1 ? "day" : "days"}</span>
              </label>
            )
          })}
        </div>
        <div className="total">{totalCards} cards</div>
      </div>
      <div className="cards-body">
        {cards.length > 0 ? (
          cards.map((card, index) => <Card key={index} source={source} card={card} index={index} />)
        ) : (
          <p style={{ color: "white", marginTop: "30px" }}>No report cards found</p>
        )}
      </div>
    </div>
  )
}

export default Cards
