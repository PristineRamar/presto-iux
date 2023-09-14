import React from "react";
// import Chart from "react-apexcharts";
import "../styles/table.css";

const ChartParser = ({ message, chatType }) => {
  //console.log("chatType", chatType);
  let parsedMessage;
  let updatedOptions;
  
  // function capitalizeFirstLetter(str) {
  //   return str
  //     .split(' ')
  //     .map(word => word.charAt(0).toUpperCase() + word.slice(1))
  //     .join(' ');
  // }

  if (chatType === "line" || chatType === "bar" || chatType === "table" || chatType === "pie" ) {
    parsedMessage = JSON.parse(message);

    if (chatType !== "table") {
      if (parsedMessage.options.xaxis) {
        for (let key in parsedMessage.options.xaxis) {
          const numLabels = parsedMessage.options.xaxis[key].length;
          const values = parsedMessage.options.xaxis[key];
          const maxKeyLength = Math.max(...values.map(value => value.length));
          let offset = 0;
          if(maxKeyLength > 17) {
            offset = 18
          }
          const fontSize = "15px";
          updatedOptions = {
            xaxis: {
              categories: parsedMessage.options.xaxis[key],
              tickAmount: numLabels,
              labels: {
                maxHeight: 200, 
                offsetX: offset,
                style: {
                  fontSize: fontSize,
                  fontWeight: "bold",
                },
              },
            },
            yaxis: {
              fixed: true,
              labels: {
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
