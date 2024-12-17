import React, { useState } from "react";
import "./fixme.css";
import new_order_tags from "./data/new-order-tags.json";
import cancel_order_tags from "./data/cancel-order-tags.json";
import { socketio_client } from "../../util/socketio-client";
import { useLabOptions } from "../lab/lab-context";

const FixMe = ({ terminal }) => {
  /**
   * create a draft order on page load with default values
   * @returns draft order object with keys and values
   * { "1": "SDET_OCTAURA", "15": "USD", ... }
   */
  const draft = (tags) => {
    const _draft = {};
    const _checked = {};

    tags.forEach((tag) => {
      const fixtag = tag["tag"];
      const values = tag["values"];

      _draft[fixtag] = "";
      if (values.length === 1) {
        const value = values[0];
        _draft[fixtag] = value; // set the default value if the tag has only one value for the draft order
        _checked[fixtag] = { [value]: true };
      } else if (values.length > 1) {
        values.forEach((value) => {
          _checked[fixtag] = { [value]: false };
        });
      }
    });
    // console.log(`the draft order ::: ${JSON.stringify(_draft)}`);

    return { draft_order: _draft, draft_checked: _checked };
  };

  const { draft_order, draft_checked } = draft(new_order_tags);

  const [orderType, setOrderType] = useState("new"); // new or cancel
  const [newOrder, setNewOrder] = useState(draft_order);
  const [tagChecked, setTagChecked] = useState(draft_checked);
  const { selectedOptions } = useLabOptions();

  /**
   * handle radio button change event for fix tag with an array of values
   * @param {*} event radio button click event
   * @param {*} tag fix tag value
   */
  const handle_radio_change = (event, tag) => {
    const value = event.target.value;
    console.log(`Radio button clicked: ${tag} - ${value}`);
    setNewOrder((prev_order) => ({ ...prev_order, [tag]: value }));
    setTagChecked((prev) => {
      const prev_tag_value = newOrder[tag]; // store the prevously checked value to update
      return {
        ...prev,
        [tag]: {
          ...prev[tag],
          [prev_tag_value]: false, // uncheck the previous value
          [value]: !prev[tag][value], // check the new value
        },
      };
    });
  };

  const handle_tag_input = (event, tag) => {
    setNewOrder((prev_order) => ({
      ...prev_order,
      [tag]: event.target.value,
    }));
  };

  const handle_submit = async (event) => {
    event.preventDefault();

    // const time = new Date().getTime(); // let server side set the time?
    // new_order["60"] = time; // set the transaction time for the fix order

    terminal.write(`Submitting order: ${JSON.stringify(newOrder)}\r\n`);
    terminal.write(`\x1B[1;3;31m You\x1B[0m $ `);

    await socketio_client("fixme", newOrder, terminal); // send the order to the w.socket server

    // clear the order state after submitting
    setNewOrder(draft_order);
  };

  // for debugging purposes
  // useEffect(() => { console.log(JSON.stringify(order)) }, [order]);

  const fix_suite = selectedOptions[3];
  const fixme_enabled = ["client", "dealer"].includes(fix_suite);

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
          const fix_tag = tag["tag"];
          const name = tag["name"];
          const values = tag["values"];
          const values_type = typeof values; // type of values decide if the row should display radio buttons or an input field
          const is_even = i % 2 === 0; // for row styling. even and odd rows have different background colors

          return (
            <div
              key={i}
              className={`fix-tag-row ${is_even ? "even-row" : "odd-row"}`}
            >
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
                          onChange={(event) =>
                            handle_radio_change(event, fix_tag)
                          }
                          checked={
                            tagChecked[fix_tag][value] === true &&
                            newOrder[fix_tag] === value
                          }
                        />
                        {value}
                      </label>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
        <div>
          <button
            type="submit"
            className={`button submit-button ${
              fix_suite === "client" ? "enabled" : "disabled"
            }`}
            onClick={handle_submit}
          >
            Submit
          </button>
        </div>
      </form>
    );
  };

  /**
   * display the order type selected by the user: new or cancel
   * @param {*} event
   * @returns jsx for the order type selected
   */
  const handle_order_type = (event) => {
    const order_type_before = event.target.value;
    const order_type_new = order_type_before === "new" ? "cancel" : "new";
    console.log(`Order type set to: ${order_type_new}`);
    setOrderType(order_type_new);
    if (order_type_before === "new") {
      // setOrder(draftOrder(newOrderTags));
      return (
        <div className="fix-tags">{display_fix_order(new_order_tags)}</div>
      );
    } else {
      return (
        <div className="fix-tags">{display_fix_order(cancel_order_tags)}</div>
      );
    }
  };

  return (
    <div
      className={`fixme component ${fixme_enabled ? "enabled" : "disabled"}`}
    >
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
        <span className={`order-type-label ${orderType === "new" ? "new" : "cancel"}`}>{orderType}</span>
      </div>
      {orderType === "new" && (
        <div className="fix-tags">{display_fix_order(new_order_tags)}</div>
      )}
      {orderType === "cancel" && (
        <div className="fix-tags">{display_fix_order(cancel_order_tags)}</div>
      )}
    </div>
  );
};

export default FixMe;
