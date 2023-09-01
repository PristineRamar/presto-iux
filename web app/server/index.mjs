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
 
  //REST API call
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
		
    //    res.json({
    //      message: responseData.result,
    //    });
		
		
		// const conversationId = uuidv4();
	
        const connection = await oracledb.getConnection({
          user: "DEV_FOODLION",
          password: "F#oDLioN#DEV",
          connectString: "secure.pristineinfotech.com:3541/DEVFL",
        });
	
        console.log(userDetails, " :: ", message, " :: ", conversationId, " :: ", sessionId );
        //, " :: ", responseData.result.summary, " :: ", responseData.result.meta_data);
	
		if(responseData.result.summary)
        {
          const sql = `
            INSERT INTO CONVERSATIONS (SESSIONID, CONVERSATIONID, USERDETAILS, message, Response, TYPE, METADATA, TIMESTAMP)
            VALUES (:id, :conversationId, :sender, :message, :api_response, :response_type,  :metaData, CURRENT_TIMESTAMP)
          `;
	
          const binds = {
            id: sessionId,
            conversationId: conversationId,
            sender: userDetails,
            message:message,
            api_response: JSON.stringify(removeTypeProperty(responseData.result.summary)),
             response_type: null,
              metaData: null,
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


// const responseData = {
//   result: {
//     // error_code:"parsing",
//     // error_message:"We had trouble identifying the product(s) you mentioned. Can you try rephrasing?",
//     // detail:"Got an error from DATA API",
//     // "summary": {"type": "table", "tableData1": [{"Cluster": 1, "Store Count": 4, "Store Names": "Grand Union-Warrensburg, Grand Union-Peru, Grand Union-Saranac Lake, Grand Union-Rome", "Avg. Distance In Miles": 1.5, "Median Income": 47533.82, "Urbanicity (Mode)": "Rural"}, {"Cluster": 2, "Store Count": 4, "Store Names": "Grand Union-Rutland, Grand Union-Sherrill, Grand Union-Owego, Grand Union-Cooperstown", "Avg. Distance In Miles": 2.5, "Median Income": 54767.31, "Urbanicity (Mode)": "Rural"}, {"Cluster": 3, "Store Count": 3, "Store Names": "Grand Union-Watertown, Grand Union-Cortland, Grand Union-Norwich", "Avg. Distance In Miles": 1.9, "Median Income": 59363.08, "Urbanicity (Mode)": "Suburban"}], "message": "You can download the complete data from this location E:/Users/Chavi/cluster_data.csv"}
//     "summary": "There are 1,428 Walgreens stores within 3 miles of a Rite Aid store"
//   }
// };

//         const conversationId = uuidv4();
//         // const sessionId = uuidv4();

//         const connection = await oracledb.getConnection({
//           user: "DEV_FOODLION",
//           password: "F#oDLioN#DEV",
//           connectString: "secure.pristineinfotech.com:3541/DEVFL",
//         });

//         console.log(userDetails, " :: ", message, " :: ", conversationId, " :: ", sessionId , "::", responseData.result.summary.type);
        
//         // const completeSQl;
//         if(responseData.result.summary)
//         {
//             const sql = `
//               INSERT INTO CONVERSATIONS (SESSIONID, CONVERSATIONID, USERDETAILS, message, Response, TYPE, METADATA, TIMESTAMP)
//               VALUES (:id, :conversationId, :sender, :message, :api_response, :response_type,  :metaData, CURRENT_TIMESTAMP)
//             `;

//             const binds = {
//               id: sessionId,
//               conversationId: conversationId,
//               sender: userDetails,
//               message:message,
//               api_response: JSON.stringify(removeTypeProperty(responseData.result.summary)),
//               response_type: null,
//               metaData: null,
//             };

//             if(responseData.result.summary.type){
//               binds.response_type = responseData.result.summary.type;
//             }
      
//             if (responseData.result.meta_data) {
//               binds.metaData = JSON.stringify(responseData.result.meta_data);
//             }
      
//             function removeTypeProperty(obj) {
//               if (obj && typeof obj === 'object') {
//                   const { type, ...rest } = obj;
//                   return rest;
//               }
//               return obj;
//             }
            
      
//             const result = await connection.execute(sql, binds, { autoCommit: true });
//               connection.release();
          
//               res.json({
//                 message: responseData.result,
//               });
//         }
//         else if(responseData.result.error_code){
//           const sql = `
//             INSERT INTO CONVERSATIONS (SESSIONID, CONVERSATIONID, USERDETAILS, message,  TIMESTAMP, ERROR_CODE, ERROR_MESSAGE, ERROR_DETAIL)
//             VALUES (:id, :conversationId, :sender, :message, CURRENT_TIMESTAMP, :error_code, :error_message, :detail)
//           `;

//         const binds = {
//           id: sessionId,
//           conversationId: conversationId,
//           sender: userDetails,
//           message:message,
//           error_code: responseData.result.error_code,
//           error_message: responseData.result.error_message,
//           detail: responseData.result.detail,
//         };

//   //     console.log("completeSql", completeSql);
//       const result = await connection.execute(sql, binds, { autoCommit: true });
//         connection.release();

//   res.json({
//     message: responseData.result });
//       }
// });