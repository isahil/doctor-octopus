import { useState } from "react"
import { NavLink, useLocation } from "react-router-dom"
import "./navbar.css"
import { github_icon, grafana_icon } from "../../util/icons"

const { VITE_GITHUB_LINK, VITE_GRAFANA_LINK } = import.meta.env

const NavBar = () => {
  const location = useLocation()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const nav_bars = [
    { path: "/", label: "Reports", icon: "👩🏻‍🔬" },
    { path: "/the-lab", label: "Lab", icon: "🧪" },
    // { path: "/settings", label: "Settings", icon: "⚙️" },
  ]

  const external_links = [
    {
      url: VITE_GITHUB_LINK,
      label: "GitHub Repository",
      icon: github_icon(20, 20)
    },
    {
      url: VITE_GRAFANA_LINK,
      label: "Grafana Dashboard",
      icon: grafana_icon(20, 20)
    },
  ]

  const toggle_menu = () => {
    setIsMenuOpen(!isMenuOpen)
  }

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-container">
          <img src="/img/favicon-2.ico" alt="Doctor Octopus Logo" className="logo" />
          <h1>Doctor Octopus</h1>
        </div>

        {/* Mobile menu toggle */}
        <button
          className="menu-toggle"
          onClick={toggle_menu}
          aria-expanded={isMenuOpen}
          aria-controls="navigation-menu"
        >
          <span className="hamburger"></span>
          <span className="sr-only">Menu</span>
        </button>

        <nav id="navigation-menu" className={`navigation-tabs ${isMenuOpen ? "is-open" : ""}`}>
          {nav_bars.map(({ path, label, icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
              onClick={() => setIsMenuOpen(false)}
            >
              <span className="nav-icon">{icon}</span>
              <span className="nav-label">{label}</span>
            </NavLink>
          ))}

          {/* External links section */}
          <div className="external-links">
            {external_links.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="external-link"
                title={link.label}
                aria-label={link.label}
              >
                {link.icon}
              </a>
            ))}
          </div>
        </nav>
      </div>

      <div className="current-page-indicator">
        {nav_bars.find((link) => link.path === location.pathname)?.label || "Home"}
      </div>
    </header>
  )
}

export default NavBar
