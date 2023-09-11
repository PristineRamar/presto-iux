import { config } from "dotenv";
import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import oracledb from "oracledb";
import jwt from "jsonwebtoken";
import { v4 as uuidv4 } from 'uuid';

//move this as config
const port = 1514;
const app = express();
let refreshTokens = [];
config();

app.use(express.json());
app.use(cors());

oracledb.outFormat = oracledb.OUT_FORMAT_OBJECT;

const generateAccessToken = (user) => {
  return jwt.sign(user, process.env.ACCESS_TOKEN_SECRET, {expiresIn: "2h"});
};

const generateRefreshToken = (user) => {
  return jwt.sign(user, process.env.REFRESH_TOKEN_SECRET);
};


async function fun() {
  let connection;

  //move this as config
  try {
    connection = await oracledb.getConnection({
      user: "DEV_FOODLION",
      password: "F#oDLioN#DEV",
      connectString: "secure.pristineinfotech.com:3541/DEVFL",
    });
	
	//connection = await oracledb.getConnection({
    //  user: "DEV_HANNAFORD",
    //  password: "H#AFord#DEV",
    //  connectString: "secure.pristineinfotech.com:3540/DEVHF",
    //});

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
      // console.log("result.rows[0]: ", result.rows[0]);
      if (result.rows.length > 0) {
        console.log("status:", 200);
        const auth = generateAccessToken(result.rows[0]);
        const refreshToken = generateRefreshToken(result.rows[0]);
        refreshTokens.push(refreshToken);
        result.rows = [...result.rows, { auth }];
        result.rows = [...result.rows, { refreshToken }];
        res.status(200).json(result.rows);
      }
    });

    app.post("/prestoUserValidation", (req, res) => {
      console.log("prestoUserValidation");
      const {userToken} = req.body;
      console.log("userToken", userToken);
      const sqlQuery = `SELECT user_id, password FROM user_details where user_id = (select user_id FROM user_token_details where USER_TOKEN= :userToken)`;
      const binds = {userToken };
      connection.execute(sqlQuery, binds, {}).then((result) => {
        if (result.rows.length > 0) {
          // console.log("status:", result.rows);
          // const userId = result.rows[0].USER_ID;
          res.status(200).json(result.rows);
        }
        else {
          res.status(401).json("Incorrect Token!");
        }
      });
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
  // console.log("verifyToken", authHeader);
  // console.log("authHeader", authHeader);
  if (authHeader) {
    const token = authHeader.split(" ")[1];

    jwt.verify(token, process.env.ACCESS_TOKEN_SECRET, (err, user) => {
      if (err) {
        console.log("verify token err");
        return res.status(403).json("Token is not valid!");
      }
      req.user = user;
      // console.log("req.user", req.user);
      next();
    });
  } else {
    res.status(401).json("You are not authenticated!");
  }
};


app.post("/refresh", async (req, res) => {
  // console.log("refreshTokens", refreshTokens);
  const refreshToken = req.headers.authorization;
  const refreshHeader = refreshToken.split(" ")[1];
  // console.log("refreshHeader", refreshHeader);

  //send error if there is no token or it's invalid
  if (!refreshHeader){
    return res.status(401).json("You are not authenticated!");}
  if (!refreshTokens.includes(refreshHeader)) {
    console.log("refresh token not found afaew");
    return res.status(403).json("Refresh token is not valid!");
  }
      jwt.verify(refreshHeader, process.env.REFRESH_TOKEN_SECRET, (err, user) => {
        // console.log("user", user);  
    err && console.log(err);
    refreshTokens = refreshTokens.filter((token) => token !== refreshHeader);

    const newAccessToken = generateAccessToken(user);
    const newRefreshToken = generateRefreshToken(user);

    refreshTokens.push(newRefreshToken);

    res.status(200).json({
      accessToken: newAccessToken,
      refreshToken: newRefreshToken,
    });
  });
});

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.post("/", verifyToken, async (req, res) => {
  const { userDetails, message, sessionId } = req.body;
  //console.log(message, "message");
  //console.log(userDetails, "userDetails");

  //REST API call to connect to Router
    try {
      const conversationId = uuidv4();

      const response = await fetch("http://20.228.231.91:9002/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
         body: JSON.stringify({
          userid: userDetails,
          prompt: message,
          sessionid: sessionId,
          conversationid: conversationId,
        }),
      });

        if (response.ok) {
          const responseData = await response.json();
  		    console.log("response1: ", responseData);

          const connection = await oracledb.getConnection({
            user: "DEV_FOODLION",
            password: "F#oDLioN#DEV",
            connectString: "secure.pristineinfotech.com:3541/DEVFL",
          });

          console.log(userDetails, " :: ", message, " :: ", conversationId, " :: ", sessionId );

  		if(responseData.result.summary)
          {
            const sql = `
              INSERT INTO CONVERSATIONS (SESSIONID, CONVERSATIONID, USERDETAILS, message, Response, TYPE, METADATA, TIMESTAMP, INTENT)
              VALUES (:id, :conversationId, :sender, :message, :api_response, :response_type,  :metaData, CURRENT_TIMESTAMP, :detail)
            `;

            const binds = {
              id: sessionId,
              conversationId: conversationId,
              sender: userDetails,
              message:message,
              api_response: JSON.stringify(removeTypeProperty(responseData.result.summary)),
              response_type: null,
              metaData: null,
              detail: responseData.result.detail,
            };

  		if(responseData.result.summary.type){
             binds.response_type = responseData.result.summary.type;
          }

            if (responseData.result.meta_data) {
              binds.metaData = JSON.stringify(responseData.result.meta_data);
          }

            function removeTypeProperty(obj) {
              if (obj && typeof obj === 'object') {
                  const { type, ...rest } = obj;
                  return rest;
              }
              return obj;
          }

            const result = await connection.execute(sql, binds, { autoCommit: true });
              connection.release();

              res.json({
                message: responseData.result,
              });
          }
         else if(responseData.result.error_code){
  		console.log("error test");
            const sql = `
              INSERT INTO CONVERSATIONS (SESSIONID, CONVERSATIONID, USERDETAILS, message,  TIMESTAMP, ERROR_CODE, ERROR_MESSAGE, ERROR_DETAIL)
              VALUES (:id, :conversationId, :sender, :message, CURRENT_TIMESTAMP, :error_code, :error_message, :detail)
            `;

          const binds = {
            id: sessionId,
            conversationId: conversationId,
            sender: userDetails,
            message:message,
            error_code: responseData.result.error_code,
            error_message: responseData.result.error_message,
            detail: responseData.result.detail,
          };

  		 const result = await connection.execute(sql, binds, { autoCommit: true });
           connection.release();

  		res.json({
  		message: responseData.result });
        }
        } else {
          response.console.error();
          console.log("response not received");
          const response = {
            result: {
              summary: "Retry with a different question",
            },
          };
          console.log(response.result);
          res.json({ message: response.result });
        }
      } catch (error) {
        console.error("Error occurred during fetch:", error);
        const response = {
          result: {
            summary: "We had trouble interpreting your request. Can you try again with different phrasing?",
          },
        };
        console.log(response.result);
        if(response.result.summary.includes("\"")){
          console.log("includes");
          const summaryObject = JSON.parse(response.result.summary);
          response.result.summary = summaryObject;
          console.log("response.result.summary", response.result.summary);
        }
        else {
          console.log("not includes");
        }
        res.json({ message: response.result });
      }
  });

//   const responseData = {
//     result: {
//       summary: {
//         type: "bar",
//         options: {
//           xaxis: {
//             "PRODUCT_NAME": ["ADULT INCONTINENCE","ADULT NUTRITIONAL","AP/DEODORANTS","APPAREL","APPL/DOM/HW-BASIC","AS SEEN ON TV","AUTOMOTIVE","B/E TOYS - TAX","BABY CARE","BABY DIAPERS","BAKERY","BASIC TOYS","BATH","BATTERIES","BEER","BEVERAGES","BOOKS/MAGAZINES","CALENDARS","CANDLES","CBD","CHRISTMAS CANDY","CHRISTMAS TOYS & PLUSH","COTTON & COSMETIC BAGS","DAIRY","DIAGNOSTIC/DIABETIC","DIET","DIGESTIVE HEALTH","DOLLAR SHOP","DOMESTICS/HOUSEWARES-SSNL","DSD SNACKS","EASTER CANDY","EYE/EAR CARE","FIRST AID","FITNESS","FIXTURES","FOOT CARE","FRAGRANCES","FRAMES & ALBUMS","FROZEN FOOD","GARDEN DECOR","GARDEN LIVE GOODS","GARDEN SUPPLIES","GENERAL CANDY","GNC","GREETING CARDS/GIFT ACC","HAIR CARE","HAIR CARE ACCESSORIES","HAIR COLORING","HALLOWEEN CANDY","HALLOWEEN SUNDRIES","HARDWARE","HOLIDAY","HOME ELECTRONICS","HOME ENTERTAINMENT","HOME HEALTH CARE","HOSIERY","HOUSEHOLD CHEMICALS","HOUSEHOLD CLEANING","ICE","ICE CREAM","INSECTICIDES","LIGHT BULBS","MAKEUP - EYE","MAKEUP - FACIAL","MAKEUP - LIP","MAKEUP - NAIL","MAKEUP ACCESSORIES","MISCELL DUMP-CATCH ALL","MULTI CULTURAL","NEUTROGENA COSMETICS","NEWSPAPERS","NUTRITIONAL BARS","OPTICAL","ORAL CARE","OTC/RX UNKNOWN","PAIN CARE","PAPER PRODUCTS","PERISHABLE FOODS","PERSONAL CARE APPLIANCES","PET CARE","PHOTO-CAPTURE","PLASTIC BAGS","RX LEGEND","RX OTC","SANITARY PROTECTION","SEXUAL WELL BEING","SHAVING","SHOES/SEWING","SKIN CARE","SMOKING CESSATION","SOUVENIRS","SPIRITS","SPORTING GOODS","SPORTS NUTRITION","STATIONERY","SUMMER ACCESSORIES","SUMMER FURNITURE","SUMMER TOYS","SUN CARE","SUNDRIES","TOBACCO","TRIAL SIZE","UMBRELLAS","UNKNOWN","UPPER RESPIRATORY","VALENTINE CANDY","VITAMINS/HERBALS","WAREHOUSE GROCERY","WAREHOUSE SNACKS","WINE","WINTER SEASONAL"]
//           },
//         },
//         series: [
//           {
//             name: "Price Index",
//             "data": [96.24,103.64,101.58,206.45,98.01,97.56,96.75,59.92,95.98,94.31,101.35,97.75,96.05,118.49,88.83,101.64,109.49,138.56,110.7,95.98,106.57,84.09,106.35,96.33,95.65,96.38,97.86,113.61,89.98,99.25,104.84,99.04,100.72,106.01,100.2,97.28,103.59,99.83,102.17,100.53,150.12,98.4,95.42,84.92,126.24,96.96,98.34,102.24,102.12,50.7,110.54,101.29,121.24,44.7,106.44,105.74,96.14,103.39,76.45,97.48,102.14,102.51,101.92,101.72,102.61,106.57,107.8,119.79,98.77,100.56,94.5,104.16,98.16,99.54,132.34,100.33,97.63,95.13,100.01,104.18,135.17,125.57,43.45,84.79,95.98,96.23,98.95,101.46,94.65,96.75,110.01,85.7,86.08,96.15,100.14,101.77,78.04,87.15,99.81,131.65,93.34,109.63,129.48,76.5,99.48,137.16,97.15,100.13,103.63,92.61,109.27]
//           },
//         ],
//       },
//       meta_data: {
//         timeframe: "06/04/2023 - 09/02/2023",
//         locations: ["CHAIN","Zone","store"],
//         products: ["GROCERY","hair","oral care"],
//       },
//     },
//   };
//   res.json({ message: responseData.result });
// });
