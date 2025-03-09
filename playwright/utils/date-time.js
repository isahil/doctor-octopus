export const get_est_date_time = () => {
  const options = { timeZone: "America/New_York" };
  const date = new Date()
    .toLocaleString("en-US", options)
    .replace(/\//g, "-")
    .replace(/,/g, "")
    .replace(/ /g, "_")
    .replace(/:/g, "-");

  return date;
};
