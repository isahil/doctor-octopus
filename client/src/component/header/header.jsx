import "./header.css"

const Header = ({ source, toggle_source }) => {
  return (
    <div className="app-header">
      <div className="source">
        <p className="source-header">{source}</p>
        <label>
          <input type="checkbox" onClick={toggle_source} />
        </label>
      </div>
      <div className="title">
        <h1>Doctor Octopus</h1>
      </div>
    </div>
  )
}

export default Header
