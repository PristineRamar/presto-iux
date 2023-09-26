import React, {memo,useState, useEffect} from "react";
import { FaUser } from "react-icons/fa";
import Chart from "react-apexcharts";
import Table from "./Table";
import "../styles/table.css";
import ChartParser from "./ChartParser";
import ChartWidthCalculator from "../utils/ChartWidthCalculator";
import gptAvatar from "../assets/Images/KaiLogo.png";

const ICON_SIZE = 20;

const ChatMessage = memo(({ message, metadata, chatType, visible, intent }) => {
  console.log("chatType", chatType);
  console.log("intent", intent);
  console.log("metadata", metadata);

  const { updatedOptions, parsedMessage, chartType, maxKeyLength } = ChartParser({ message: message.message, chatType }); // Call ChartParser to get options and series

  const [chartWidth, setChartWidth] = useState("100%");

  const renderList = (items) => (
    <ul className="text-container" style={{ listStyleType: "none" }}>
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );

  return (
    <>
      <div className={`chat-message ${message.user === "gpt" && "chatgpt"}`}>
        <div className="chat-message-allign">
          <div className={`avatar ${message.user === "gpt" && "chatgpt"}`}>
            {/* user input human logo */}
            {message.user === "me" && (<FaUser size={ICON_SIZE} color="#2780dd" />)}
            {/* ai response react logo */}
            {message.user === "gpt" && (<img src={gptAvatar} alt="GPT Avatar" width="35" height="35" />)}
          </div>

          <div className={`message ${message.user === "gpt" && "chatgpt"}`}>
            {message.user === "gpt" && metadata && chartType !== "graph" && (
              <div className="chartTitle">
                <p>
                  <span className="chartlist"><b>Location:</b></span>
                  <span> </span>
                  <span className="chartlist">{metadata.locations.join(", ")}</span>
                  <span className="chartlist"><span> </span><b>Product:</b></span>
                  <span> </span>
                  <span className="chartlist">{metadata.products.join(", ")}</span>
                  <span className="chartlist"><span> </span><b>Time Frame:</b></span>
                  <span> </span>
                  <span className="chartlist">{metadata.timeframe}</span>
                </p>
              </div>
            )}
            <ChartWidthCalculator
              chatType={chatType}
              updatedOptions={updatedOptions}
              setChartWidth={setChartWidth}
              maxKeyLength={maxKeyLength}
            />
            {chatType === "array" ? (
              renderList(message.message.split(","))
            ) : chatType === "newLine" ? (
              renderList(message.message.split("\n"))
            ) : chatType === "line" || chatType === "bar" || chatType === "pie" ? (
              <>
                <div className="chartheading"><p>{intent}</p></div>
                {/* .split("_") // Split the string into words
              .map((word) => word.charAt(0).toUpperCase() + word.slice(1)) // Capitalize the first letter of each word
              .join(" ")}</p></div> */}
                {metadata && (
                  <div className="chartTitle">
                    {Array.isArray(metadata.locations) ? (
                      <p>
                        <span className="chartdetails">Location:</span>
                        <span> </span>
                        <span className="chartlist">{metadata.locations.join(", ")}</span>
                        <span> </span>
                        <span className="chartdetails">Product:</span>
                        <span> </span>
                        <span className="chartlist">{metadata.products.join(", ")}</span>
                        <span> </span>
                        <span className="chartdetails"> Time Period :</span>
                        <span> </span>
                        <span className="chartlist">{metadata.timeframe}</span>
                        <span> </span>
                        {metadata.competitor && (
                          <span>
                            <span className="chartdetails">{" "}Competitor(s):</span>
                            <span> </span>
                            <span className="chartlist">{metadata.competitor.join(", ")}</span>
                          </span>
                        )}
                        <span> </span>
                        {metadata.index_type && (
                          <span>
                            <span className="chartdetails">{" "}Index Type:</span>
                            <span> </span>
                            <span className="chartlist">{metadata.index_type.join(", ")}</span>
                          </span>
                        )}
                      </p>
                    ) : (
                      <p>
                        <span className="chartlist">Location:</span>{" "}
                        <span className="chartlist">{metadata.locations}</span>{" "}
                        <span>{"    "}</span>
                        <span className="chartdetails">, Product:</span>{" "}
                        <span className="chartlist">{metadata.products}</span>{" "}
                        <span>{"    "}</span>
                        <span className="chartdetails">, Time Period:</span>{" "}
                        <span className="chartlist">{metadata.timeframe}</span>{" "}
                        <span>{"    "}</span>
                        <span className="chartdetails">{" "}Competitor(s):</span>{" "}
                        <span className="chartlist">{metadata.competitor}</span>
                        <span>{"    "}</span>
                        <span className="chartdetails">{" "}Index Type:</span>{" "}
                        <span className="chartlist">{metadata.index_type}</span>
                      </p>
                    )}
                  </div>
                )}
                <Chart
                  options={updatedOptions}
                  series={parsedMessage.series}
                  type={chatType}
                  width={chartWidth}
                  height="400px"
                />
              </>
            ) : chatType === "table" ? (
              <div className="table-container">
                <Table data={parsedMessage.tableData1} />
              </div>
            ) : (
              <p className={!visible ? "text-container" : "text-container-with-sidebar"}> {message.message} </p>
            )}
          </div>
        </div>
      </div>
      <div style={{ margin: "8px 0", width: "8px" }}></div>
    </>
  ); 
});

export default ChatMessage;
