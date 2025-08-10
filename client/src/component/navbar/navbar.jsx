import { useState } from "react"
import { NavLink, useLocation } from "react-router-dom"
import "./navbar.css"

const NavBar = () => {
  const location = useLocation()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const navLinks = [
    { path: "/", label: "Reports", icon: "👩🏻‍🔬" },
    { path: "/the-lab", label: "Lab", icon: "🧪" },
    // { path: "/settings", label: "Settings", icon: "⚙️" },
  ]

  const toggleMenu = () => {
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
          onClick={toggleMenu}
          aria-expanded={isMenuOpen}
          aria-controls="navigation-menu"
        >
          <span className="hamburger"></span>
          <span className="sr-only">Menu</span>
        </button>

        <nav id="navigation-menu" className={`navigation-tabs ${isMenuOpen ? "is-open" : ""}`}>
          {navLinks.map(({ path, label, icon }) => (
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
        </nav>
      </div>

      <div className="current-page-indicator">
        {navLinks.find((link) => link.path === location.pathname)?.label || "Home"}
      </div>
    </header>
  )
}

export default NavBar
