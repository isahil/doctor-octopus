import React, { useState } from "react"
import "./fixme.css"
import new_order_tags from "./data/new-order-tags.json"
import cancel_order_tags from "./data/cancel-order-tags.json"
import { useSocketIO } from "../../util/socketio-context"
import { useLabOptions } from "../lab/lab-context"
import { useTerminal } from "../xterm/terminal-context"

const FixMe = () => {
  const { terminal } = useTerminal()
  /**
   * create a draft order on page load with default values
   * @returns draft order object with keys and values
   * { "1": "SDET_OCTAURA", "15": "USD", ... }
   */
  const draft = (tags) => {
    const _draft = {}
    const _checked = {}

    tags.forEach((tag) => {
      const fixtag = tag["tag"]
      const values = tag["values"]

      _draft[fixtag] = ""
      if (values.length === 1) {
        const value = values[0]
        _draft[fixtag] = value // set the default value if the tag has only one value for the draft order
        _checked[fixtag] = { [value]: true }
      } else if (values.length > 1) {
        values.forEach((value) => {
          _checked[fixtag] = { [value]: false }
        })
      }
    })
    // console.log(`the draft order ::: ${JSON.stringify(_draft)}`);

    return { draft_order: _draft, draft_checked: _checked }
  }

  const { draft_order, draft_checked } = draft(new_order_tags)

  const [orderType, setOrderType] = useState("new") // new or cancel
  const [newOrder, setNewOrder] = useState(draft_order)
  const [tagChecked, setTagChecked] = useState(draft_checked)
  const { selectedOptions } = useLabOptions()
  const { sio } = useSocketIO()

  const restriction_tags = ["7762", "9691", "9692"] // tags related to restrictions block
  const nopartyid_tags = ["447", "448", "452"] // tags related to nopartyid block

  /**
   * handle radio button change event for fix tag with an array of values
   * @param {*} event radio button click event
   * @param {*} tag fix tag value
   */
  const handle_radio_change = (event, tag) => {
    const value = event.target.value
    console.log(`Radio button clicked: ${tag} - ${value}`)
    setNewOrder((prev_order) => ({ ...prev_order, [tag]: value }))
    setTagChecked((prev) => {
      const prev_tag_value = newOrder[tag] // store the prevously checked value to update
      return {
        ...prev,
        [tag]: {
          ...prev[tag],
          [prev_tag_value]: false, // uncheck the previous value
          [value]: !prev[tag][value], // check the new value
        },
      }
    })
  }

  const handle_tag_input = (event, tag) => {
    setNewOrder((prev_order) => ({
      ...prev_order,
      [tag]: event.target.value,
    }))
  }

  const handle_submit = async (event, fix_side = "client") => {
    sio.off("fixme") // Remove existing listener to avoid duplicate logs
    event.preventDefault()

    const order = newOrder
    const restrictions = []
    const nopartyid = []

    Object.keys(order).forEach((key) => {
      if (restriction_tags.includes(key)) {
        restrictions.push({ [key]: order[key] })
        delete order[key]
      } else if (nopartyid_tags.includes(key)) {
        nopartyid.push({ [key]: order[key] })
        delete order[key]
      }
    })

    order["9690"] = restrictions // add the restrictions to the order
    order["453"] = nopartyid // add the nopartyid to the order
    terminal.write(`\r\n\x1B[1;3;32m Doc:\x1B[1;3;37m Submitting: ${JSON.stringify(order)}\r\n`)

    sio.on("fixme", (data) => {
      terminal.write(`\r\n\x1B[1;3;33m Server:\x1B[1;3;36m ${JSON.stringify(data)} \r\n`)
    })
    sio.emit("fixme", order) // send the data to the w.s. server
    // clear the order state after submitting
    setNewOrder(draft_order)
  }

  // for debugging purposes
  // useEffect(() => { console.log(JSON.stringify(order)) }, [order]);

  const fix_suite = selectedOptions[3]
  const fixme_enabled = ["client", "dealer"].includes(fix_suite)

  /**
   * display fix tags based on the fix-tags.json file values
   * if the values are string, it will display input field
   * if the values are array, it will display button with dropdown
   * @returns
   */
  const display_fix_order = (tags) => {
    return (
      <form>
        {tags.map((tag, i) => {
          const fix_tag = tag["tag"]
          const name = tag["name"]
          const values = tag["values"]
          const values_type = typeof values // type of values decide if the row should display radio buttons or an input field
          const is_even = i % 2 === 0 // for row styling. even and odd rows have different background colors
          let enabled = "enabled" // used to disable the fix tag row if order restrictions are set to false
          if (restriction_tags.includes(fix_tag))
            enabled = tagChecked["6499"]["Y"] === true ? "enabled" : "disabled"

          return (
            <div key={i} className={`fix-tag-row ${is_even ? "even-row" : "odd-row"} ${enabled}`}>
              <div className="tag-label">
                <p>{fix_tag}</p>
              </div>
              <div className="name-label">
                <p>{name}</p>
              </div>
              <div className="value-label">
                {values_type === "string" && !tag["values"] ? (
                  // if the tag value is an empty string handle input field display
                  <div className="tag-input">
                    <input
                      key={i}
                      type="text"
                      placeholder={name}
                      value={newOrder[fix_tag] || ""}
                      onChange={(event) => handle_tag_input(event, fix_tag)}
                    />
                  </div>
                ) : (
                  <div className="tag-radio">
                    {values.map((value, j) => (
                      <label key={j}>
                        <input
                          type="radio"
                          className="radio"
                          name={fix_tag}
                          value={value}
                          onChange={(event) => handle_radio_change(event, fix_tag)}
                          checked={
                            tagChecked[fix_tag][value] === true && newOrder[fix_tag] === value
                          }
                        />
                        {value}
                      </label>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        })}
        <div>
          <button
            type="submit"
            className={`button submit-button ${fix_suite === "client" ? "enabled" : "disabled"}`}
            onClick={(event) => handle_submit(event)}
          >
            Submit
          </button>
        </div>
      </form>
    )
  }

  /**
   * display the order type selected by the user: new or cancel
   * @param {*} event
   * @returns jsx for the order type selected
   */
  const handle_order_type = (event) => {
    const order_type_before = event.target.value
    const order_type_new = order_type_before === "new" ? "cancel" : "new"
    console.log(`Order type set to: ${order_type_new}`)
    setOrderType(order_type_new)
    if (order_type_before === "new") {
      return <div className="fix-tags">{display_fix_order(new_order_tags)}</div>
    } else {
      return <div className="fix-tags">{display_fix_order(cancel_order_tags)}</div>
    }
  }

  return (
    <div className={`fixme component ${fixme_enabled ? "enabled" : "disabled"}`}>
      <div className="fixme-header">
        <div className="fixme-title">FIXME</div>
        <div className="order-type">
          <label className="rocker rocker-small">
            <input
              className="toggle-input"
              type="checkbox"
              value={orderType}
              // defaultChecked="true"
              onClick={(e) => handle_order_type(e)}
            />
            <span className="switch-left">X</span>
            <span className="switch-right">O</span>
          </label>
        </div>
        <span className={`order-type-label ${orderType === "new" ? "new" : "cancel"}`}>
          {orderType}
        </span>
      </div>
      {orderType === "new" && <div className="fix-tags">{display_fix_order(new_order_tags)}</div>}
      {orderType === "cancel" && (
        <div className="fix-tags">{display_fix_order(cancel_order_tags)}</div>
      )}
    </div>
  )
}

export default FixMe
