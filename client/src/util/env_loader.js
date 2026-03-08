const {
  VITE_API_BASE_URL,
  VITE_MAIN_SERVER_URL_DEV,
  VITE_MAIN_SERVER_URL_PROD,
  VITE_MAIN_SERVER_HOST,
  VITE_MAIN_SERVER_PORT,
  VITE_FIXME_SERVER_HOST,
  VITE_FIXME_SERVER_PORT,
} = import.meta.env

const normalize_base_url = (url) => String(url || "").replace(/\/+$/, "")

const get_default_dev_main_api_url = () => {
  const host = VITE_MAIN_SERVER_HOST || "127.0.0.1"
  const port = VITE_MAIN_SERVER_PORT || "8000"
  return `http://${host}:${port}`
}

const get_main_api_base_url = () => {
  if (VITE_API_BASE_URL) {
    return normalize_base_url(VITE_API_BASE_URL)
  }

  if (import.meta.env.PROD) {
    return normalize_base_url(
      VITE_MAIN_SERVER_URL_PROD || "https://doctor-api.internal.octaura.com"
    )
  }

  return normalize_base_url(VITE_MAIN_SERVER_URL_DEV || get_default_dev_main_api_url())
}

const fixme_server_host = VITE_FIXME_SERVER_HOST || "127.0.0.1"
const fixme_server_port = VITE_FIXME_SERVER_PORT || "8001"

export const runtime_config = {
  main_api_base_url: get_main_api_base_url(),
  fixme_server_host,
  fixme_server_port,
}
