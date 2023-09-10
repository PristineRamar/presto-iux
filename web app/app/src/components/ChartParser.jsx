import React from "react";
// import Chart from "react-apexcharts";
import "../styles/table.css";

const ChartParser = ({ message, chatType }) => {
  let parsedMessage;
  let updatedOptions;
  let series


  if (chatType === "line" || chatType === "bar" || chatType === "table" || chatType === "pie") {
    parsedMessage = JSON.parse(message);

    if (chatType !== "table") {
        if(parsedMessage.options.xaxis){
            for (let key in parsedMessage.options.xaxis) {
                      updatedOptions = {
                          xaxis: {
                            categories: parsedMessage.options.xaxis[key]
                          }
                        };
                  }
        }
      else updatedOptions = parsedMessage.options;
      
      updatedOptions.chart = {
        id: "basic-bar",
        zoom: { enabled: false },
        toolbar: { show: true },
      };
      updatedOptions.dataLabels = {
        enabled: false,
      };
      updatedOptions.colors = ["#E91E63","#FF9800","#064687","#340b7c89","#09b40989","#b409a389",];
    }

    console.log("parsedMessage", parsedMessage);
    console.log("updatedOptions", updatedOptions);
}

  return { updatedOptions,  parsedMessage};
};

export default ChartParser;
