import React, { useEffect, useState } from "react";
import Card from "./card";
import "./cards.css";
import { SERVER_HOST, SERVER_PORT } from "../../index";

const Cards = ({ source }) => {
  const [cards, setCards] = React.useState([]);
  const [totalCards, setTotalCards] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * fetch cards data from the FASTAPI server. TODO: Implement the WebSocket subscription logic
   */
  const get_cards = async () => {
    setIsLoading(true); // set loading to true before the fetch request starts
    try {
      const response = await fetch(
        `http://${SERVER_HOST}:${SERVER_PORT}/cards?source=${source}`
      );
      const data = await response.json();
      setTotalCards(data.length);
      const filtered_data = data.filter(
        (card) => card.json_report.suites.length > 0
      ); // filter out cards that did not run any test suites
      console.log(
        `Total ${source} cards: ${data.length} | filtered cards: ${filtered_data.length}`
      );
      setCards(filtered_data);
    } catch (error) {
      console.error("Error fetching cards data:", error);
    } finally {
      setIsLoading(false); // set loading to false after the fetch request completes
    }
  };

  useEffect(() => {
    get_cards();
  }, [source]); // fetch cards data when the source changes

  if (isLoading) {
    return (
      <div className="loading-screen">
        <p>Loading...</p>
      </div>
    );
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
        <div className="total">{totalCards} cards</div>
      </div>
      <div className="cards-body">
        {cards.length > 0 ? (
          cards.map((card, index) => (
            <Card key={index} source={source} card={card} index={index} />
          ))
        ) : (
          <p style={{ color: "white", marginTop: "30px" }}>No report cards found in your local directory</p>
        )}
      </div>
    </div>
  );
};

export default Cards;
