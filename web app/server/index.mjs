import { config } from "dotenv";
import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import oracledb from "oracledb";
import jwt from "jsonwebtoken";

//move this as config
const port = 1514;
const app = express();
config();

app.use(express.json());
app.use(cors());

oracledb.outFormat = oracledb.OUT_FORMAT_OBJECT;

async function fun() {
  let connection;

  //move this as config
  try {
    connection = await oracledb.getConnection({
      user: "DEV_HANNAFORD",
      password: "H#AFord#DEV",
      connectString: "secure.pristineinfotech.com:3540/DEVHF",
    });

    // connection = await oracledb.getConnection({
    //   user: "PRESTO_IUX",
    //     password: "PR#IUX#2023",
    //     connectString: "secure7.pristineinfotech.com:7781/IUX",
    //   });

    console.log("Connected to the database.");

    app.use(express.json());
    app.post("/login", async (req, res) => {
      const { username, password } = req.body;
      const sqlQuery = `SELECT * FROM user_details where user_id= :username and password= :password`;
      const binds = { username, password };
      const result = await connection.execute(sqlQuery, binds, {});
      if (result.rows.length > 0) {
        console.log("status:", 200);
        const auth = jwt.sign(result.rows[0], process.env.ACCESS_TOKEN_SECRET, {expiresIn: "2h",});
        result.rows = [...result.rows, { auth }];
        res.status(200).json(result.rows);
      }
    });
  } catch (err) {
    console.error("Error executing the query:", err);
  }
}
fun();

const server = app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});

const verifyToken = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (authHeader) {
    const token = authHeader.split(" ")[1];

    jwt.verify(token, process.env.ACCESS_TOKEN_SECRET, (err, user) => {
      if (err) {
        return res.status(403).json("Token is not valid!");
      }

      req.user = user;
      next();
    });
  } else {
    res.status(401).json("You are not authenticated!");
  }
};

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.post("/", verifyToken, async (req, res) => {
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
//        body: JSON.stringify({ 
//         userid: userDetails, 
//         prompt: message, }),
//     });
  
//       if (response.ok) {
//         const responseData = await response.json();
//         console.log("response: ", responseData.result);
//         res.json({
//           message: responseData.result,
//         });
//       } else {
//         response.console.error();
//         console.log("response not received");
//         const response = {
//           result: {
//             summary: "Retry with a different question",
//           },
//         };
//         console.log(response.result);
//         res.json({ message: response.result });
//       }
//     } catch (error) {
//       console.error("Error occurred during fetch:", error);
//       const response = {
//         result: {
//           summary: "Error occurred during fetch, please retry",
//         },
//       };
//       console.log(response.result);
//       res.json({ message: response.result });
//     }
// });

const response = {
  result: {
    meta_data: {
              locations: ["ZP00620"],
              products: ["UPPER RESPIRATORY"],
              timeframe: "05/07/2023 - 06/24/2023",
            },
    summary: "Today we access IUX though a separate URL. However, we can have a link or an option to access IUX on price review and category analysis screen. While there are certain actions like overriding prices, updating cost, and updating recommendation that can be performed by interacting through IUX. /n Pradeep and team are working on it. On the other hand generic info queries, kvi analysis can be performed through dialogues though CA. Dan and Priyanka are working on these cases. So the IUX link can be enabled in these 2 modules to start with."
  },
};
res.json({
  message: response.result });

});

//******************************************************************* */
// app.js
// import express from "express";
// import cors from "cors";
// import bodyParser from "body-parser";
// import {loginHandler, verifyToken } from "./auth.mjs";
// import {queryHandler} from "./query.mjs";

// const port = 1514;
// const app = express();
// // const { loginHandler, verifyToken } = pkg;
// // const { queryHandler } = chatpkg;

// app.use(express.json());
// app.use(cors());

// app.post("/login", loginHandler);
// app.post("/", verifyToken, queryHandler);

// app.use(bodyParser.json());
// app.use(bodyParser.urlencoded({ extended: false }));

// const server = app.listen(port, () => {
//   console.log(`Example app listening at http://localhost:${port}`);
// });
