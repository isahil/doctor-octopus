import React, { useEffect, useState } from "react";
import Card from "./card";
import "./cards.css";
import { SERVER_HOST, SERVER_PORT } from "../../index";

const Cards = ({ source }) => {
  const [cards, setCards] = React.useState([]);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * fetch cards data from the FASTAPI server. TODO: Implement the WebSocket subscription logic
   */
  const get_cards = async () => {
    try {
      const response = await fetch(
        `http://${SERVER_HOST}:${SERVER_PORT}/reports?source=${source}`
      );
      const data = await response.json();
      console.log(`Total ${source} cards: ${data.length}`);
      setCards(data);
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
        <img
          src="/img/refresh.png"
          alt="refresh"
          className="refresh-button"
          onClick={get_cards}
        />
      </div>
      <div className="cards-body">
        {cards.map((card, index) => (
          <Card key={index} source={source} card={card} index={index} />
        ))}
      </div>
    </div>
  );
};

export default Cards;
