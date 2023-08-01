import fetch from "node-fetch";
import express from "express";
import cors from "cors";
import bodyParser from "body-parser";

const port = 1514;
const app = express();

app.use(express.json());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cors());

app.post("/", async (req, res) => {
  const { message } = req.body;
  console.log(message, "message");

  //REST API call
  // try {
  //   const response = await fetch("http://20.228.231.91:8000/query", {
  //     method: "POST",
  //     headers: {
  //       "Content-Type": "application/json",
  //     },
  //     body: JSON.stringify({ prompt: message }),
  //   });
// 
//     if (response.ok) {
//       const responseData = await response.json();
//       console.log("response: ", responseData.result);
//       res.json({
//         message: responseData.result,
//       });
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
// });

const response =
  {
    "result": {
      "meta_data": {
          "locations": ["ZP00620"],
          "products": ["UPPER RESPIRATORY"],
          "timeframe": "05/07/2023 - 06/24/2023"
      },
      "summary": 'The items that had a cost change in Zone 620 during the last three weeks are:\n' +
      '1. 100 GRAND SNGL 1.5Z\n' +
      '2. 48 ROCHER TABLET SHIPPER\n' +
      '3. AFRIN EX MO TWIN 2X15ML\n' +
      '4. AFRIN ND EX MST 15+5ML\n' +
      '5. AFRIN ND SINUS 15ML\n' +
      '6. AFRIN ND SVR CONG 15+5ML\n' +
      '7. AFRIN NO DR EX MST SP 15ML\n' +
      '8. AFRIN NO DR SPR 2X15ML\n' +
      '9. AFRIN NO DR SV CNG SP 15ML\n' +
      '10. AFRIN NO DRIP NIGHT 15ML'     }
  }

console.log(response, "response");
res.json({
  message: response.result });
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});
