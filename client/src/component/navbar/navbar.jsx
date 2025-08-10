import "./navbar.css"
import { NavLink } from "react-router-dom"

export default function NavBar({ source, toggle_source }) {
  return (
    <header className="header">
      <div className="header-content">
        <nav className="navigation-tabs">
          <NavLink to="/" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
            Reports
          </NavLink>
          <NavLink
            to="/the-lab"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            Fixme
          </NavLink>
        </nav>

        <div className="logo-container">
          {/* <img src="/public/img/favicon-2.ico" alt="Doctor Octopus Logo" className="logo"/> */}
          <h1>Doctor Octopus</h1>
        </div>
      </div>
    </header>
  )
}
