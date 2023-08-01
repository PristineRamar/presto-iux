// query.js
import fetch from "node-fetch";

export async function queryHandler(req, res) {
  const { userDetails, message } = req.body;
  console.log(message, "message");
  console.log(userDetails, "userDetails");

  //REST API call
//   try {
//     const response = await fetch("http://20.228.231.91:8000/query", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify({ prompt: message }),
//     });

//     if (response.ok) {
//       const responseData = await response.json();
//       console.log("response: ", responseData.result);
//       res.json({ message: responseData.result });
//     } else {
//       response.console.error();
//       console.log("response not received");
//       const response = {
//         result: {
//           summary: "Retry with a different question",
//         },
//       };
//       console.log(response.result);
//       res.json({ message: response.result });
//     }
//   } catch (error) {
//     console.error("Error occurred during fetch:", error);
//     const response = {
//       result: {
//         summary: "Error occurred during fetch, please retry",
//       },
//     };
//     console.log(response.result);
//     res.json({ message: response.result });
//   }

const response = {
    result: {
      meta_data: {
        locations: ["ZP00620"],
        products: ["UPPER RESPIRATORY"],
        timeframe: "05/07/2023 - 06/24/2023",
      },
      summary:
        "The items that had a cost change in Zone 620 during the last three weeks are:",
    },
  };

  console.log(response, "response");
  res.json({message: response.result});
}
