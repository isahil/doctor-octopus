import "./navbar.css"
import { NavLink } from "react-router-dom"

export default function NavBar() {
  return (
    <nav className="navigation-tabs">
      <NavLink to="/" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
        Reports
      </NavLink>
      <NavLink
        to="/the-lab"
        className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
      >
        The Lab
      </NavLink>
    </nav>
  )
}
