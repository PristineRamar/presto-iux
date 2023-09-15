import React, { useEffect } from "react";

const ChartWidthCalculator = ({ chatType, updatedOptions, setChartWidth, maxKeyLength }) => {
  useEffect(() => {
    // Calculate the chart width based on the number of X-axis labels
    if (chatType === "line") {
      const numLabels =
        updatedOptions.xaxis && updatedOptions.xaxis.categories
          ? updatedOptions.xaxis.categories.length
          : 1; // Default to 1 if no categories

      console.log("numLabels", numLabels);

      // Calculate the label width based on the label content
      const labelWidth = 50; // Default label width
      const labelSpacing = 10; // Default label spacing
      const minWidth = 1000; // Minimum chart width

      // Calculate the chart width based on labels and spacing
      const calculatedWidth = numLabels * labelWidth + (numLabels - 1) * labelSpacing;

      // Set the chart width dynamically with a minimum width constraint
      setChartWidth(`${Math.max(calculatedWidth, minWidth)}px`);
    } else 
    if (chatType === "bar" || chatType === "pie") {
      // For bar and pie charts, you can use your existing code
      let minWidthPerLabel = 75; // Minimum width per label
      let additionalWidth ;// Additional width for padding
      if(maxKeyLength > 10) 
        additionalWidth = 1000;
      else
      additionalWidth = 300;

      const numLabels =
        updatedOptions.xaxis && updatedOptions.xaxis.categories ? updatedOptions.xaxis.categories.length: 1; // Default to 1 if no categories

      console.log("numLabels", numLabels);
      const calculatedWidth = numLabels * minWidthPerLabel + additionalWidth;
      // Set the chart width dynamically
      setChartWidth(`${calculatedWidth}px`);
    }
  }, [chatType, updatedOptions]);

  return null; // This component doesn't render anything
};

export default ChartWidthCalculator;
