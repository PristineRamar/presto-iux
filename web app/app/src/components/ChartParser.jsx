import React from "react";
// import Chart from "react-apexcharts";
import "../styles/table.css";

const ChartParser = ({ message, chatType }) => {
  //console.log("chatType", chatType);
  let parsedMessage;
  let updatedOptions;
  let chartType;
  let maxKeyLength;
  
  // function capitalizeFirstLetter(str) {
  //   return str
  //     .split(' ')
  //     .map(word => word.charAt(0).toUpperCase() + word.slice(1))
  //     .join(' ');
  // }

  function formatYAxisLabels(value) {
    // Use toLocaleString to add commas and toFixed to round to 0 decimal places
    return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
  }

  if (chatType === "line" || chatType === "bar" || chatType === "table" || chatType === "pie" ) {
    parsedMessage = JSON.parse(message);

    if (chatType !== "table") {
      chartType = "graph";
      if (parsedMessage.options.xaxis) {
        for (let key in parsedMessage.options.xaxis) {
          const numLabels = parsedMessage.options.xaxis[key].length;
          const values = parsedMessage.options.xaxis[key];
          maxKeyLength = Math.max(...values.map(value => value.length));

          // // Calculate the minimum and maximum values from the data
          // const minValue = Math.min(...dataSeries);
          // const maxValue = Math.max(...dataSeries); 

          // // Calculate a buffer value (e.g., 10%) to add some padding to the Y-axis range
          // const buffer = 0.1; // You can adjust this as needed

          // // Calculate the adjusted minimum and maximum values
          // const adjustedMinValue = minValue - buffer * (maxValue - minValue);
          // const adjustedMaxValue = maxValue + buffer * (maxValue - minValue);

          let rotate = 0;
          let maxHeight = 200;
          if(maxKeyLength > 17 && numLabels > 10) {
            rotate = -90
          }
          if(maxKeyLength > 25) {
            maxHeight=300
          }
          const fontSize = "15px";
          updatedOptions = {
            xaxis: {
              categories: parsedMessage.options.xaxis[key],
              tickAmount: numLabels,
              labels: {
                rotate: rotate, 
                maxHeight: maxHeight, 
                // offsetX: offset,
                style: {
                  fontSize: fontSize,
                  fontWeight: "bold",
                },
              },
            },
            yaxis: {
              // min: adjustedMinValue, // Set the minimum Y-axis value dynamically
              // max: adjustedMaxValue, // Set the maximum Y-axis value dynamically
              fixed: true,
              floating: false,
              labels: {
                // formatter: function(val) {return val.toFixed(0);},
                //formatter: formatYAxisLabels,
                formatter: function(value) {
                  var val = Math.abs(value)
                  if (val >= 1000000) {
                    val = (val / 1000000).toFixed(1) + " M";
                  }
                  else if (val >= 1000) {
                    val = (val / 1000).toFixed(0) + ' K'
                  }
                  return val
                },
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
        enabled: false,
        formatter: function (val) {
          // Customize the formatting of data labels as needed
          //return val.toFixed(0); // Format the value to display two decimal places
          var val1 = Math.abs(val)
          if (val1 >= 1000000) {
            val1 = (val1 / 1000000).toFixed(1) + " M";
          }
          else if (val1 >= 1000) {
            val1 = (val1 / 1000).toFixed(0) + ' K'
          }
          return val1
        },
        style: {
          fontSize: "15px", 
          fontWeight: "bold",
          colors: ["#121212"], // Set the color of data labels here
        },
      };
      updatedOptions.colors = ["#1389fd","#FF9800","#20855e","#340b7c89","#09b40989","#b409a389",];

    }

    console.log("parsedMessage", parsedMessage);
    console.log("updatedOptions", updatedOptions);
}

  return { updatedOptions,  parsedMessage, chartType, maxKeyLength};
};

export default ChartParser;
