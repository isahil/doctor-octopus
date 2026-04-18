import postgres from "postgres";
import "dotenv/config";
import { get_db_username, get_db_password, get_db_host, get_db_port, get_db_name } from "./env_loader.js";

const sql = postgres({
	host: get_db_host(),
	port: get_db_port(),
	database: get_db_name(),
	username: get_db_username(),
	password: get_db_password(),

	// Additional configuration options
	max: 20, // Maximum number of connections
	idle_timeout: 20, // Close connection after 20 seconds of inactivity
	connect_timeout: 10, // Connection timeout in seconds

	// Transform column names from snake_case to camelCase
	// transform: {
	// 	column: {
	// 		to: postgres.camel,
	// 		from: postgres.snake,
	// 	},
	// },

	// Debug mode (set to true for development)
	debug: process.env.NODE_ENV === "development",
});
export default sql;
