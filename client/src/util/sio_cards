const get_cards_from_sio = async () => {
  // Socket.IO implementation to get cards data. When enabling this, make sure to disable the REST API call in the useEffect hook and add sio as a dependency.
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
      // if (card.json_report.suites.length <= 0) return // filter out cards that did not run any test suites
      setTotalCards((prevTotalCards) => prevTotalCards + 1)
      setCards((prevCards) => [...prevCards, card])
    })
    sio.emit("cards", filters) // emit a message to the server to fetch cards data over WebSocket

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
