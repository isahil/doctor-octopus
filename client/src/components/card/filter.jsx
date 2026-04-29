import "./filter.css"

const Filters = ({ filter, cardFilters, setCardFilters }) => {
  const { name, options } = filter

  const handle_filter_change = (e) => {
    const { value } = e.target
    console.log(`clicked ${name} filter:  ${value}`)
    setCardFilters((prevFilter) => ({ ...prevFilter, [name]: value }))
  }

  return (
    <div className="options-wrapper">
      <div className="options-placeholder" style={{ visibility: "hidden" }}>
        <label className="option-wrapper" style={{ display: "block" }}>
          <div className="option">
            <span className={`filter ${name}-${cardFilters[name]}`}>{cardFilters[name]}</span>
          </div>
        </label>
      </div>
      <div className="options-dropdown">
        {options
          .sort((a, b) =>
            a[name] === cardFilters[name] ? -1 : b[name] === cardFilters[name] ? 1 : 0
          )
          .map((option, i) => {
            return (
              <label key={i} className="option-wrapper">
                <input
                  key={i}
                  type="radio"
                  name={`${name}-${option}`}
                  value={option}
                  onChange={handle_filter_change}
                  checked={cardFilters[name] == option}
                ></input>
                <div className="option">
                  <span className={`filter ${name}-${option}`}>{option}</span>
                </div>
              </label>
            )
          })}
      </div>
    </div>
  )
}

export default Filters
