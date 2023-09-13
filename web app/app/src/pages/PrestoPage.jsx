import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from 'react-router-dom';

function PrestoPage() {
  const { tokentoPrestoPage } = useParams();
  console.log("tokentoPrestoPage:" + tokentoPrestoPage);
  const navigate = useNavigate();
  const [status, setStatus] = useState(false);
  const [data1, setData1] = useState(null);
  const [token, setToken] = useState('');

  const REACTAPP_APIURL = process.env.REACT_APP_API_URL;
  const REACTAPP_PRESTOURL = process.env.REACT_APP_PRESTO_URL;
  const REACT_APPHOST = process.env.REACT_APP_HOST;

  useEffect(() => {
    console.log("Fetching userDetails");
    //Get the token from the query parameter in the URL
    const urlParams = new URLSearchParams(window.location.search);
    //const tokenFromURL = urlParams.get('token');
    const tokenFromURL = tokentoPrestoPage;
    console.log("tokenFromURL:" + tokenFromURL);
    setToken(tokenFromURL);
    console.log("urlParams:" + urlParams);
    // const tokenFromURL = '6yiy1A7LxAaCoYApUkZrrE8PqbQlZLfz';

    if (tokenFromURL) {
      setToken(tokenFromURL);

      // Send the token to the Node.js server for validation
      fetch(REACTAPP_PRESTOURL, {
      // fetch(`http://localhost:1514/prestoUserValidation`,{ 
    //   fetch(`http://secure.pristineinfotech.com:4026/prestoUserValidation`,{ 
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userToken: tokenFromURL,
        }),
      })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log("data: " + JSON.stringify(data));
            const userId = data[0].USER_ID;
            const password = data[0].PASSWORD;
            console.log("userId: " + userId);
            console.log("password: " + password);

            // let response =  
            fetch(REACTAPP_APIURL, {
            // fetch("http://secure.pristineinfotech.com:4026/login", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  username: userId,
                  password: password,
                }),
              })
              .then((response) => {
                return response.json();
            }).then((data) => {
                console.log("data: " + JSON.stringify(data));
                        setStatus(true);
                        setData1(data)
            });
        })
        .catch(error => {
          console.error('Error validating token:', error);
        });
    }
    
  }, []);

  useEffect(() => {
    if (status === true) {

      console.log('status is true', data1[0].USER_ID);
      localStorage.setItem("user",JSON.stringify(data1[0]));
      localStorage.setItem("auth",JSON.stringify(data1[1]));
      localStorage.setItem("refreshToken",JSON.stringify(data1[2]));
      localStorage.setItem("userToken",JSON.stringify(token));
      navigateToAiChat(data1[0].USER_ID);
    }
  }, [data1, status]);

  const navigateToAiChat = (userId) => {
    navigate(`/KAIStage/aichat?userId=${userId}`);
    //navigate(process.env.REACT_APP_AI_REDIRECT`?userId=${userId}`);
  };

//   return (
//     <div>
//       {" "}
//       PrestoPage
//       <div>Status: {status ? "Valid" : "Invalid"}</div>
//       <div>Data: {data1 ? JSON.stringify(data1) : "No data"}</div>
//     </div>
//   );
}

export default PrestoPage;
