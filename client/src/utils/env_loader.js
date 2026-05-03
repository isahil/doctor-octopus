const {
  VITE_API_BASE_URL,
  VITE_MAIN_SERVER_URL_DEV,
  VITE_MAIN_SERVER_URL_PROD,
  VITE_MAIN_SERVER_HOST,
  VITE_MAIN_SERVER_PORT,
  VITE_FIXME_BASE_URL,
  VITE_FIXME_SERVER_URL_DEV,
  VITE_FIXME_SERVER_URL_PROD,
  VITE_FIXME_SERVER_HOST,
  VITE_FIXME_SERVER_PORT,
  VITE_ALLOWED_HOSTS,
} = import.meta.env

const normalize_base_url = (url) => String(url || "").replace(/\/+$/, "")

const get_default_dev_main_api_url = () => {
  const host = VITE_MAIN_SERVER_HOST
  const port = VITE_MAIN_SERVER_PORT
  return `http://${host}:${port}`
}

const get_default_dev_fixme_api_url = () => {
  const host = VITE_FIXME_SERVER_HOST
  const port = VITE_FIXME_SERVER_PORT
  return `http://${host}:${port}`
}

const get_main_api_base_url = () => {
  if (VITE_API_BASE_URL) {
    return normalize_base_url(VITE_API_BASE_URL)
  }

  if (import.meta.env.PROD && VITE_MAIN_SERVER_URL_PROD) {
    return normalize_base_url(VITE_MAIN_SERVER_URL_PROD)
  }

  return normalize_base_url(VITE_MAIN_SERVER_URL_DEV || get_default_dev_main_api_url())
}

const get_fixme_api_base_url = () => {
  if (VITE_FIXME_BASE_URL) {
    return normalize_base_url(VITE_FIXME_BASE_URL)
  }

  if (import.meta.env.PROD && VITE_FIXME_SERVER_URL_PROD) {
    return normalize_base_url(VITE_FIXME_SERVER_URL_PROD)
  }

  return normalize_base_url(VITE_FIXME_SERVER_URL_DEV || get_default_dev_fixme_api_url())
}

export const allowed_hosts = VITE_ALLOWED_HOSTS || ".com"

export const runtime_config = {
  main_api_base_url: get_main_api_base_url(),
  fixme_api_base_url: get_fixme_api_base_url(),
  allowed_hosts,
}
