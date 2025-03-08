import "./filter.css"

const Filters = ({ filter_conf, filter, setFilter }) => {
  const { name, options } = filter_conf

  const handle_filter_change = (e) => {
    const { value } = e.target
    console.log(`clicked ${name} filter:  ${value}`)
    setFilter(value)
  }

  return (
    <div className="option-wrapper">
      {options.map((option, i) => {
        return (
          <label key={i} className={`${name} name-option`}>
            <input
              key={i}
              type="radio"
              name={`${name}-${option}`}
              value={option}
              onChange={handle_filter_change}
              checked={filter == option}
            ></input>
            <span className={`filter ${name}-${option}`}>{option}</span>
            <span className="filter text">{name}</span>
          </label>
        )
      })}
    </div>
  )
}

export default Filters
