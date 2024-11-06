import React, { useState, useEffect } from "react";
import "./fixme.css";
import new_order_tags from "./fixTags.json";

const FixMe = () => {
  const [order, setOrder] = useState({});
  const [orderType, setOrderType] = useState("new"); // new or cancel

  /**
   * create a draft order on page load with default values
   * @returns draft order object with keys and values
   * { "notional": "", "price": "", ... }
   */
  const draftOrder = () => {
    const order = {};
    new_order_tags.forEach((fix_tag) => {
      const tag = fix_tag["tag"];
      order[tag] = fix_tag["values"].length === 1 ? fix_tag["values"][0] : "";
    });
    // console.log(JSON.stringify(order));
    return order;
  };

  /**
   * display the order type selected by the user: new or cancel
   * @param {*} event
   * @returns jsx for the order type selected
   */
  const handleOrderType = (event) => {
    console.log(event.target.value);
    setOrderType(event.target.value);
    if (event.target.value === "new") {
      setOrder(draftOrder());
      return (
        <div className="fix-tags">{displayNewOrderFixTags(new_order_tags)}</div>
      );
    } else {
      return <div className="fix-tags">{displayCancelOrderFixTags()}</div>;
    }
  };

  const handleTagInput = (event, tag) => {
    setOrder((prevOrder) => ({ ...prevOrder, [tag]: event.target.value }));
  };

  const handleRadioChange = (event, tag) => {
    setOrder((prevOrder) => ({ ...prevOrder, [tag]: event.target.value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log("Submitting order", order);
  };

  useEffect(() => {
    setOrder(draftOrder());
  }, []);

  // for debugging purposes
  // useEffect(() => {
  //   console.log(JSON.stringify(order));
  // }, [order]);

  /**
   * display fix tags based on the fix-tags.json file values
   * if the values are string, it will display input field
   * if the values are array, it will display button with dropdown
   * @returns
   */
  const displayNewOrderFixTags = (tags) => {
    return (
      <form>
        {tags.map((fix_tag, i) => {
          const tag = fix_tag["tag"];
          const name = fix_tag["name"];
          const values = fix_tag["values"];
          const valuesLength = Array.isArray(values) ? values.length : 0;
          const isEven = i % 2 === 0;

          return (
            <div
              key={i}
              className={`fix-tag-row ${isEven ? "even-row" : "odd-row"}`}
            >
              <div className="tag-label">
                <p>{tag}</p>
              </div>
              <div className="name-label">
                <p>{name}</p>
              </div>
              <div className="value-label">
                {typeof fix_tag["values"] === "string" && !fix_tag["values"] ? (
                  // if the tag value is an empty string handle input field display
                  <div className="tag-input">
                    <input
                      key={i}
                      type="text"
                      placeholder={name}
                      value={order[tag] || ""}
                      onChange={(event) => handleTagInput(event, tag)}
                    />
                  </div>
                ) : (
                  <div className="tag-radio">
                    {fix_tag["values"].map((value, j) => (
                      <label key={j}>
                        <input
                          type="radio"
                          name={tag}
                          value={value}
                          checked={valuesLength === 1}
                          onChange={(event) => handleRadioChange(event, tag)}
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
            className="submit-button"
            onClick={(event) => handleSubmit(event)}
          >
            Submit
          </button>
        </div>
      </form>
    );
  };

  const displayCancelOrderFixTags = () => {
    return (
      <div>
        <label>COMING SOON...</label>
      </div>
    );
  };

  return (
    <div className="fixme">
      <div className="fixme-header">
        <div className="fixme-title">Fix Me</div>
        <div className="order-type">
          <label>
            <input
              type="radio"
              value="new"
              name="order"
              checked={orderType === "new"}
              onChange={handleOrderType}
            />
            New
          </label>
          <label>
            <input
              type="radio"
              value="cancel"
              name="order"
              checked={orderType === "cancel"}
              onChange={handleOrderType}
            />
            Cancel
          </label>
        </div>
      </div>
      {orderType === "new" && (
        <div className="new-fix-tags">
          {displayNewOrderFixTags(new_order_tags)}
        </div>
      )}
      {orderType === "cancel" && (
        <div className="cancel-fix-tags">{displayCancelOrderFixTags()}</div>
      )}
    </div>
  );
};

export default FixMe;
