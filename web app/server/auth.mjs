// auth.js
import { config } from "dotenv";
import oracledb from "oracledb";
import jwt from "jsonwebtoken";

config();
oracledb.outFormat = oracledb.OUT_FORMAT_OBJECT;

export async function loginHandler(req, res) {
  let connection;
  try {
    connection = await oracledb.getConnection({
        user: "DEV_HANNAFORD",
        password: "H#AFord#DEV",
        connectString: "secure.pristineinfotech.com:3540/DEVHF",
    });

    console.log("Connected to the database.");

    const { username, password } = req.body;
    const sqlQuery = `SELECT * FROM user_details where user_id= :username and password= :password`;
    //   const binds = { id: "prestolive", pass: "Prest0livE" };
    const binds = { username, password };
    const result = await connection.execute(sqlQuery, binds, {});
    if (result.rows.length > 0) {
      const auth = jwt.sign(result.rows[0], process.env.ACCESS_TOKEN_SECRET, {
        expiresIn: "2h",
      });
      result.rows = [...result.rows, { auth }];
      console.log(result.rows);
      res.status(200).json(result.rows);
    }
  } catch (err) {
    console.error("Error executing the query:", err);
    res.sendStatus(500);
  } finally {
    if (connection) {
      try {
        await connection.close();
      } catch (err) {
        console.error("Error closing the connection:", err);
      }
    }
  }
}

export function verifyToken(req, res, next) {
  let token = req.headers.authorization;
  if (token) {
    token = token.split(" ")[1];
    jwt.verify(token, process.env.ACCESS_TOKEN_SECRET, (err, valid) => {
      if (err) {
        res.sendStatus(403).send("Token Expired");
      } else {
        next();
      }
    });
  } else {
    res.sendStatus(401).send("Please try with a valid token");
  }
}
