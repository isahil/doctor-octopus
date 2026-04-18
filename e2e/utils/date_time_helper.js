export const get_est_date_time = () => {
  // %m-%d-%Y_%I-%M-%S-%f_%p
	const options = { timeZone: "America/New_York" };
	const now = new Date();

	// Convert to EST and extract components manually to include milliseconds
	const est_now = new Date(now.toLocaleString("en-US", options));

	// Format: MM-DD-YYYY_HH-MM-SS-MMMMMM_AM/PM
	const month = String(est_now.getMonth() + 1).padStart(2, "0");
	const day = String(est_now.getDate()).padStart(2, "0");
	const year = est_now.getFullYear();

	// Convert to 12-hour format
	const hours12 = est_now.getHours() % 12 || 12;
	const hours = String(hours12).padStart(2, "0");
	const minutes = String(est_now.getMinutes()).padStart(2, "0");
	const seconds = String(est_now.getSeconds()).padStart(2, "0");

	// Convert to microseconds (6 digits) to match Python's %f format
	const microseconds = String(now.getMilliseconds() * 1000).padStart(6, "0");

	const ampm = est_now.getHours() >= 12 ? "PM" : "AM";

	return `${month}-${day}-${year}_${hours}-${minutes}-${seconds}-${microseconds}_${ampm}`;
};
