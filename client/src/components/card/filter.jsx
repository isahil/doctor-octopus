import "./filter.css"

const Filters = ({ filter_config, filters, setFilter }) => {
  const { name, options } = filter_config

  const handle_filter_change = (e) => {
    const { value } = e.target
    console.log(`clicked ${name} filter:  ${value}`)
    setFilter((prevFilter) => ({ ...prevFilter, [name]: value }))
  }

  return (
    <div className="options-wrapper">
      {options
        .sort((a, b) => (a[name] === filters[name] ? -1 : b[name] === filters[name] ? 1 : 0))
        .map((option, i) => {
          return (
            <label key={i} className="option-wrapper">
              <input
                key={i}
                type="radio"
                name={`${name}-${option}`}
                value={option}
                onChange={handle_filter_change}
                checked={filters[name] == option}
              ></input>
              <div className="option">
                <span className={`filter ${name}-${option}`}>{option}</span>
              </div>
            </label>
          )
        })}
    </div>
  )
}

export default Filters
