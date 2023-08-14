import { config } from "dotenv";
import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import oracledb from "oracledb";
import jwt from "jsonwebtoken";

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
  const { userDetails, message } = req.body;
  console.log(message, "message");
  // console.log(userDetails, "userDetails");

  //REST API call
  // try {
//     const response = await fetch("http://20.228.231.91:9000/query", {
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
//         console.log("response1: ", responseData.result);
// 		 if(responseData.result.summary.includes("\"")){
// 			console.log("includes");
// 			const summaryObject = JSON.parse(responseData.result.summary);
// 			responseData.result.summary = summaryObject;
// 			console.log("responseData.result.summary", responseData.result.summary);
// 		}

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
//       if(response.result.summary.includes("\"")){
//         console.log("includes");
//         const summaryObject = JSON.parse(response.result.summary);
//         response.result.summary = summaryObject;
//         console.log("response.result.summary", response.result.summary);
//       }
//       else {
//         console.log("not includes");
//       }
//       res.json({ message: response.result });
//     }
// });

const response = {
  result: {
   "meta_data": {
            "locations": [
                "CHAIN"
            ],
            "products": [
                "F-SARGENTO STRING CHS 9OZ 4575",
                "F-SARGENTO STICKS 6516",
                "F-SARGENTO SLICES 1304",
                "F-SARGENTO SHRED 8OZ  53",
                "F-Cabot cuts 7oz",
                "F-Cabot Cottage Cheese 16oz",
                "F-CABOT SOUR CREAM 16OZ",
                "F-CABOT SLICES 1299",
                "F-CABOT SHREDS 8OZ 208"
            ],
            "timeframe": "04/02/2023 - 07/01/2023"
        },
        "summary": "{\"type\": \"line\", \"options\": {\"xaxis\": {\"cal_year_week_no\": [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]}}, \"series\": [{\"name\": \"reg-price_CBT_2_STT_FRMRS_SHRD_REG_CT\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_4%_COTTAGE_CHEESE\", \"data\": [3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49]}, {\"name\": \"reg-price_CBT_4CHSE_MEXICAN_SHRED\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_ARTSN_PZA_SHRED_FINE_CUT\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_CHSE_ITALIAN_SHRED\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_COLBYJACK_CRKR_CUT\", \"data\": [4.19, 4.19, 4.19, 4.19, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_FIERY_JACK_SHRED_REG_CUT\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_HUNTER_CHEDDAR_SHRED\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_MAC__CHEESE_SHRED_REG_CUT\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_MEX_FANCY_SHRED_THK_CUT\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_MILD_WHT_CHED_SLC_STACKED\", \"data\": [4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_MNTRY_JCK_SHRD_REG_CT\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_MOZZ_SHRD_THK_CT_PRT_SKM\", \"data\": [4.39, 4.39, 4.39, 4.39, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_MUENSTER_SHINGLED_SLICES\", \"data\": [4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_NFAT_COT_CHS\", \"data\": [3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49, 3.49]}, {\"name\": \"reg-price_CBT_NY_XSHRP_YLLW_CHDR\", \"data\": [4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_PEPPERJACK_CRKR_CUT\", \"data\": [4.19, 4.19, 4.19, 4.19, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_PERPPERJCK_SLC\", \"data\": [4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_SER_SHARP_WH_CHED_CRKRCUT\", \"data\": [4.19, 4.19, 4.19, 4.19, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_SER_SHARP_YEL_CHED_CRKRCUT\", \"data\": [4.19, 4.19, 4.19, 4.19, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_SERSLY_SHRP_WHT_MINI\", \"data\": [4.19, 4.19, 4.19, 4.19, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_SHARP_WHT_CHED_CRKRCUT\", \"data\": [4.19, 4.19, 4.19, 4.19, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_SHARP_WHT_CHED_SLC_STACKED\", \"data\": [4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_SHRED_MOZZARELLA\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_SHRP_50%_LT_WHT_CHED_SHRD\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_SHRP_WHT_CHD_SHRD_REG_CT\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_SHRP_YL_CHD_SHRD_REG_CT\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_SOUR_CREAM_LT\", \"data\": [3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.39, 3.39, 3.39]}, {\"name\": \"reg-price_CBT_SOUR_CREAM_REG\", \"data\": [3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.39, 3.39, 3.39]}, {\"name\": \"reg-price_CBT_SR_SHRP_WH_CHD_SHRD_THK\", \"data\": [4.39, 4.39, 4.39, 4.39, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_SWISS_SHINGLED_SLICES\", \"data\": [4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_SWISS_SLICES_STACKED\", \"data\": [4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_VRMT_SSHRP_WCHDR\", \"data\": [4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_CBT_WM_MOZZ_SHREDS\", \"data\": [4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59, 4.59]}, {\"name\": \"reg-price_CBT_X-SHARP_WHT_CHED_CRKRCUT\", \"data\": [4.19, 4.19, 4.19, 4.19, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39, 4.39]}, {\"name\": \"reg-price_SARG_CHEDDAR_CHS_SLICES\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_EXTRA_SHRP_CHEDD_JACK\", \"data\": [6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79]}, {\"name\": \"reg-price_SARG_OTB_MLD_CHEDDR_PK\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_PPRJK_SLC_W_HABANERO\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_RF_4CHS_MEX_SHRD\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_RF_DELI_STYLE_MED_CHEDD\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_RF_MOZZ_SHRD\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_RF_SHRP_CHDR_SHRD\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_RS_GOUDA_SLCS\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRD_4_CHS_MEXICAN\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRD_NTRL_MOZZ\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRD_NTRL_SHRP_CHDR\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_6_CHS_ITL_8Z\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_ART_DBL_CH\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_ART_MOZZ\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_ART_MXCN\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_ART_PARM_GST_5Z\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_CB_4CHS_PIZ\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_CB_4ST_CHD\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_CB_TACO_GST\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_CB_TACO_GST_8Z\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_CHED_JACK\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_OB_MILD_CHD_FIN\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_OB_MOZZ\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_OB_XSH_CHD\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SHRED_SHP_CHD\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLCD_NTRL_AGED_WHT_CHDR\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLCD_NTRL_BBY_SWISS\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLCD_NTRL_CLBY_JK\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLCD_NTRL_MED_CHDR\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLCD_NTRL_MOZZ\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLCD_NTRL_MUENSTER\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLCD_NTRL_PROV\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLCD_NTRL_SHRP_CHDR\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLCD_NTRL_THN_MD_CHDR\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLCD_NTRL_THN_PROV\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLCD_NTRL_THN_SWISS\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLICED_DELI_RF_PROVOLONE\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLICED_NAT_THIN_RF_SWISS\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLICED_THIN_DELI_AGED_SWI\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLICED_ULTRA_THIN_PEP_JAC\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SLICED_ULTRA_THIN_SHRP_CH\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_SRGNT_FN_MNT_JCK_SHRD\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SARG_STICKS_NTRL_BLND_CHDR_MOZ\", \"data\": [6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79]}, {\"name\": \"reg-price_SARG_STRNG_NTRL_LIGHT_MOZZ\", \"data\": [7.39, 7.39, 7.39, 7.39, 7.39, 7.39, 7.39, 7.39, 7.39, 7.39, 7.39, 7.39, 7.39]}, {\"name\": \"reg-price_SARG_STX_NTRL_CLBY_JK\", \"data\": [6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79, 6.79]}, {\"name\": \"reg-price_SARG_UT_THIN_COLBY_JK_SL\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}, {\"name\": \"reg-price_SRGNTO_TRAD_4_MEX_SHRD\", \"data\": [4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99, 4.99]}]}"  },
};

if(response.result.summary.includes("\"")){
  console.log("includes");
  const summaryObject = JSON.parse(response.result.summary);
  response.result.summary = summaryObject;
  console.log("response.result.summary", response.result.summary);
}
else {
  console.log("not includes");
}

res.json({
  message: response.result });
});