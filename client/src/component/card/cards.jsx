import React, { useEffect, useState } from "react";
import Card from "./card";
import "./cards.css";

const Cards = ({ source }) => {
  const [cards, set_cards] = React.useState([]);
  const [is_loading, set_is_loading] = useState(true);

  const getCards = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/reports?source=${source}`
      );
      const data = await response.json();
      console.log(`Total ${source} cards: ${data.length}`);
      set_cards(data);
    } catch (error) {
      console.error("Error fetching cards data:", error);
    } finally {
      set_is_loading(false);
    }
  };

  useEffect(() => {
    getCards();
  }, [source]);

  if (is_loading) {
    return (
      <div className="loading-screen">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="cards-component">
      {cards.map((card, index) => (
        <Card key={index} source={source} card={card} index={index}/>
      ))}
    </div>
  );
};

export default Cards;
