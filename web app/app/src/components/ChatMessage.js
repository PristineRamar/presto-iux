import React, {memo,useState, useEffect} from "react";
import { FaUser } from "react-icons/fa";
import Chart from "react-apexcharts";
import Table from "./Table";
import "../styles/table.css";
import ChartParser from "./ChartParser";
import ChartWidthCalculator from "../utils/ChartWidthCalculator";

const ICON_SIZE = 20;

const ChatMessage = memo(({ message, metadata, chatType, visible, intent }) => {
  console.log("chatType", chatType);

  const { updatedOptions, parsedMessage } = ChartParser({ message: message.message, chatType }); // Call ChartParser to get options and series

  const [chartWidth, setChartWidth] = useState("100%");

  const renderList = (items) => (
    <ul className="text-container" style={{ listStyleType: "none" }}>
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );

  return (
    <div className={`chat-message ${message.user === "gpt" && "chatgpt"}`}>
      <div className="chat-message-allign">
        <div className={`avatar ${message.user === "gpt" && "chatgpt"}`}>
          {/* user input human logo */}
          {message.user === "me" && <FaUser size={ICON_SIZE} color="#2780dd" />}
          {/* ai response react logo */}
          {message.user === "gpt" && (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="44"
              height="44"
              viewBox="0 0 44 44"
            >
              <defs>
                <clipPath id="clip-path">
                  <rect
                    id="Rectangle_172280"
                    data-name="Rectangle 172280"
                    width="44"
                    height="44"
                    fill="#f7f7f7"
                  />
                </clipPath>
                <linearGradient
                  id="linear-gradient"
                  x1="1.105"
                  y1="1.262"
                  x2="1.068"
                  y2="0.033"
                  gradientUnits="objectBoundingBox"
                >
                  <stop offset="0" stopColor="#1baff8" />
                  <stop offset="1" stopColor="#0f56b5" />
                </linearGradient>
              </defs>
              <g
                id="Group_178055"
                data-name="Group 178055"
                transform="translate(3837 4953)"
              >
                <g
                  id="Group_177946"
                  data-name="Group 177946"
                  transform="translate(-3837 -4953)"
                  opacity="0.9"
                >
                  <g
                    id="Group_177861"
                    data-name="Group 177861"
                    transform="translate(0 0)"
                  >
                    <g
                      id="Group_177860"
                      data-name="Group 177860"
                      clipPath="url(#clip-path)"
                    >
                      <path
                        id="Path_91604"
                        data-name="Path 91604"
                        d="M249,229.5a22,22,0,1,1-22,22,22,22,0,0,1,22-22"
                        transform="translate(-227 -229.499)"
                        fill="#f7f7f7"
                      />
                    </g>
                  </g>
                </g>
                <g
                  id="Group_178021"
                  data-name="Group 178021"
                  transform="translate(-836.188 1394.028)"
                >
                  <g id="Group_177997" data-name="Group 177997">
                    <g
                      id="Group_177993"
                      data-name="Group 177993"
                      transform="translate(737 -1199)"
                    >
                      <g id="Group_177948" data-name="Group 177948">
                        <path
                          id="Path_91772"
                          data-name="Path 91772"
                          d="M43.734,260.5c.008.1.021.189.021.275q0,6.531.008,13.063a.382.382,0,0,1-.227.389c-1.153.646-2.3,1.307-3.44,1.968-1,.582-2,1.164-3.008,1.746l-3.824,2.212-1.2.7a.285.285,0,0,1-.062.014c0-.055-.011-.1-.011-.152-.013-2.956-.019-5.909-.043-8.862a.582.582,0,0,1,.339-.623c.689-.365,1.36-.766,2.036-1.157.716-.414,1.427-.836,2.145-1.248q1.623-.932,3.251-1.863c.474-.271.946-.546,1.424-.815a.3.3,0,0,0,.17-.289q0-1.922.026-3.842a.233.233,0,0,1,.091-.17c.757-.446,1.514-.885,2.306-1.341m-2.425,8.363c-.116.058-.193.1-.269.137l-1.57.9-2.989,1.719-1.932,1.115c-.086.05-.163.093-.161.221.015,1.182.024,2.363.035,3.545,0,.043.009.086.016.15.065-.033.116-.052.156-.078,1.065-.62,2.129-1.244,3.2-1.863q1.709-.987,3.425-1.964a.205.205,0,0,0,.116-.21q-.019-1.164-.026-2.328v-1.351"
                          transform="translate(-3760.751 -5399.292)"
                          fill="url(#linear-gradient)"
                        />
                        <path
                          id="Path_91773"
                          data-name="Path 91773"
                          d="M61.137,347.341a1.457,1.457,0,0,1-.133.1q-1.913,1.1-3.826,2.212c-.716.414-1.426.839-2.14,1.257-.633.371-1.266.743-1.9,1.1a.288.288,0,0,1-.233.014q-1.616-.916-3.223-1.848c-1.121-.65-2.237-1.305-3.358-1.957-.815-.476-1.64-.947-2.457-1.427a.34.34,0,0,0-.388,0c-.733.426-1.47.844-2.212,1.265-.37.212-.738.428-1.112.636a.219.219,0,0,1-.181.01q-1.118-.641-2.227-1.294a.825.825,0,0,1-.084-.069c.327-.2.639-.39.956-.574.487-.282.978-.554,1.466-.835q2.111-1.214,4.221-2.432c1.017-.589,2.03-1.185,3.048-1.775.622-.36,1.248-.711,1.87-1.071a.32.32,0,0,1,.369,0c1.088.635,2.184,1.255,3.274,1.885q2.224,1.281,4.443,2.575l3.743,2.167c.026.015.049.034.09.063m-15.03-2.061c.279.173.527.335.785.483.987.568,1.979,1.129,2.965,1.7q1.508.869,3.011,1.746c.072.042.13.084.226.028q1.531-.907,3.067-1.8c.038-.022.072-.052.116-.084a.309.309,0,0,0-.052-.056l-1.349-.782L51.64,344.63c-.68-.394-1.367-.775-2.041-1.177a.322.322,0,0,0-.381,0c-.782.466-1.568.923-2.354,1.385-.246.144-.489.29-.753.447"
                          transform="translate(-3765.379 -5464.08)"
                          fill="url(#linear-gradient)"
                        />
                        <path
                          id="Path_91774"
                          data-name="Path 91774"
                          d="M104.474,259.243c.363.2.7.369,1.02.554l3.656,2.1c1.07.614,2.133,1.24,3.216,1.829a.545.545,0,0,1,.317.582c-.013,2.127-.013,4.253-.013,6.377v3.875a.274.274,0,0,0,.1.2q1.423.845,2.855,1.675c.167.1.333.2.507.277a.219.219,0,0,1,.139.233c-.009.682-.015,1.365-.021,2.047v.582c-.274-.147-.527-.275-.774-.416q-1.24-.709-2.475-1.426-2.289-1.326-4.577-2.656-1.892-1.094-3.79-2.177a.286.286,0,0,1-.154-.281q.006-1.226,0-2.453V259.243m2.437,4.181v7.811a.214.214,0,0,0,.1.222q1.549.878,3.092,1.763c.039.022.082.036.137.061v-.466q.008-1.992.016-3.984c0-1.124.009-2.25.006-3.376a.267.267,0,0,0-.116-.192c-.738-.428-1.481-.849-2.224-1.27l-1.011-.571"
                          transform="translate(-3819.424 -5398.271)"
                          fill="url(#linear-gradient)"
                        />
                      </g>
                    </g>
                  </g>
                </g>
              </g>
            </svg>
          )}
        </div>
        <div className="message">
          <ChartWidthCalculator
              chatType={chatType}
              updatedOptions={updatedOptions}
              setChartWidth={setChartWidth}
            />
          {chatType === "array" ? (
            renderList(message.message.split(","))
          ) : chatType === "newLine" ? (
            renderList(message.message.split("\n"))
          ) : chatType === "line" || chatType === "bar" || chatType === "pie" ? (
            <>
            <div className = "chartheading"><p>{intent}</p></div>
              {/* .split("_") // Split the string into words
              .map((word) => word.charAt(0).toUpperCase() + word.slice(1)) // Capitalize the first letter of each word
              .join(" ")}</p></div> */}
             {metadata && (<div className = "chartTitle">
             {Array.isArray(metadata.locations) ? (
               <p>
                   <span className="chartdetails">Zone(s):</span> {metadata.locations.join(", ")} 
                   <span className="chartdetails">, Product(s):</span> {metadata.products.join(", ")}
                   <span className="chartdetails">, Time Period:</span> {metadata.timeframe}</p>) : (
               <p><span className="chartdetails">Zone(s):</span> {metadata.locations} <span className="chartdetails">, Product(s):</span> {metadata.products}
               <span className="chartdetails">, Time Period:</span>  {metadata.timeframe}</p>)}
               </div>)}
            <Chart
              options={updatedOptions}
              series={parsedMessage.series}
              type={chatType}
              width={chartWidth} //"100%"
              // width="2000px"
              height="400px"
            /></>
          ) : chatType === "table" ? (
            <div className="table-container">
                <Table data={parsedMessage.tableData1} />
            </div>
          ) : (
            <p className={!visible ? "text-container" : "text-container-with-sidebar"}>{message.message}</p>)}
        </div>
      </div>
      {message.user === "gpt" && metadata && (
        <div className="metadata">
          {Array.isArray(metadata.locations) ? (
            <p>Location: {metadata.locations.join(", ")}</p>
          ) : (
            <p>Location: {metadata.locations}</p>
          )}
          {Array.isArray(metadata.products) ? (
            <p>Product: {metadata.products.join(", ")}</p>
          ) : (
            <p>Product: {metadata.products}</p>
          )}
          <p>Timeframe: {metadata.timeframe}</p>
        </div>
      )}
    </div>
  );
});

export default ChatMessage;
