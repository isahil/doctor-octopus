import "./filter.css"

const Filters = ({ filter_conf, filter, setFilter }) => {
  const { name, options } = filter_conf

  const handle_filter_change = (e) => {
    const { value } = e.target
    console.log(`clicked ${name} filter:  ${value}`)
    setFilter((prevFilter) => ({ ...prevFilter, [name]: value }))
  }

  return (
    <div className={`${name} options-wrapper`}>
      {options
        .sort((a, b) => (a[name] === filter[name] ? -1 : b[name]  === filter[name] ? 1 : 0))
        .map((option, i) => {
          return (
            <label key={i} className={`${name} option-wrapper`}>
              <input
                key={i}
                type="radio"
                name={`${name}-${option}`}
                value={option}
                onChange={handle_filter_change}
                checked={filter[name] == option}
              ></input>
              <div className="option">
                <span className={`filter ${name}-${option}`}>{option}</span>
                {/* <span className="text">{name}</span> */}
              </div>
            </label>
          )
        })}
    </div>
  )
}

export default Filters
