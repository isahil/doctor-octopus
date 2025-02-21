const transformData = (clients, dealers) => {
  const transformedUsers = {}

  clients.forEach((client, index) => {
    const { counterparty_details, counterparty_id, counterparty_users } = client
    const baseKey = `client${index + 1}`

    counterparty_users.forEach((email, userIndex) => {
      const userKey = `${baseKey}_${userIndex + 1}`
      transformedUsers[userKey] = {
        email: email,
        counterparty_id: counterparty_id,
        short_name_counterparty: counterparty_details.COUNTERPARTY_SHORT_NAME,
        long_name_counterparty: counterparty_details.COUNTERPARTY_LONG_NAME,
        first_name: email.split("@")[0],
        last_name: "",
        sender: "",
      }
    })
  })

  dealers.forEach((dealer, index) => {
    const { counterparty_details, counterparty_id, counterparty_users } = dealer
    const baseKey = `dealer${index + 1}`

    counterparty_users.forEach((email, userIndex) => {
      const userKey = `${baseKey}_${userIndex + 1}`
      transformedUsers[userKey] = {
        email: email,
        counterparty_id: counterparty_id,
        short_name_counterparty: counterparty_details.COUNTERPARTY_SHORT_NAME,
        long_name_counterparty: counterparty_details.COUNTERPARTY_LONG_NAME,
        first_name: email.split("@")[0],
        last_name: "",
        sender: "",
      }
    })
  })

  return transformedUsers
}
