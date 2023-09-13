import React from "react";
// import Chart from "react-apexcharts";
import "../styles/table.css";

const ChartParser = ({ message, chatType }) => {
  //console.log("chatType", chatType);
  let parsedMessage;
  let updatedOptions;
  
  if (chatType === "line" || chatType === "bar" || chatType === "table" || chatType === "pie" ) {
    parsedMessage = JSON.parse(message);

    if (chatType !== "table") {
      if (parsedMessage.options.xaxis) {
        for (let key in parsedMessage.options.xaxis) {
          const numLabels = parsedMessage.options.xaxis[key].length;
          const fontSize = "15px";
          // numLabels > 50 ? "7px" : "12px";
          updatedOptions = {
            xaxis: {
              categories: parsedMessage.options.xaxis[key],
              // tickPlacement: 'on',
              tickAmount: numLabels,
              labels: {
                maxHeight: 200, 
                offsetX: 10,
                // trim: true, // Enable label trimming
                // formatter: function (val) {
                //   console.log("val", val);
                //   console.log("val.length", val.length);
                //   // Customize the label formatting and truncation as needed
                // const maxLength = 15; // Maximum length of the label
                //   console.log("maxLength", val.length > maxLength ? val.slice(0, maxLength) + "..." : maxLength);
                // return val.length > maxLength ? val.slice(0, maxLength) + "..." : val;},
                style: {
                  fontSize: fontSize,
                  fontWeight: "bold",
                },
                // maxHeight: "100px",
              },
            },
            yaxis: {
              labels: {
                // offsetX: -15,
                formatter: function(val) {return val.toFixed(0);},
                style: {
                  fontSize: fontSize,
                  fontWeight: "bold",
                },
              },
            },
          };
        }
      } else updatedOptions = parsedMessage.options;

      updatedOptions.chart = {
        id: "basic-bar",
        zoom: { enabled: false },
        toolbar: { show: true },
      };
      updatedOptions.dataLabels = {
        enabled: true,
        formatter: function (val) {
          // Customize the formatting of data labels as needed
          return val.toFixed(0); // Format the value to display two decimal places
        },
        style: {
          fontSize: "15px", 
          fontWeight: "bold",
          colors: ["#121212"], // Set the color of data labels here
        },
      };
      updatedOptions.colors = ["#1389fd","#FF9800","#064687","#340b7c89","#09b40989","#b409a389",];

    }

    console.log("parsedMessage", parsedMessage);
    console.log("updatedOptions", updatedOptions);
}

  return { updatedOptions,  parsedMessage};
};

export default ChartParser;
