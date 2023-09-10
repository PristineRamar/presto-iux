// import React, { useState, useEffect } from "react";


// function PrestoPage() {
//   // const [userToken, setUserToken] = useState(null);
//   const [status, setStatus] = useState(false);
//   const [data, setData] = useState(null);
//   const [token, setToken] = useState('');
//   const [isValid, setIsValid] = useState(false);

//   // useEffect(() => {
//   //   console.log("Fetching userToken");
//   //   fetch('http://localhost:3000/presto')
//   //   .then(response => response.json())
//   //   .then(data => {
//   //       {console.log("data: ", data)}
//   //       setUserToken(data.userToken);
//   //   })
//   //   .catch(error => {
//   //       console.error('Error fetching userToken:', error);
//   //   });
//   // }, []);

//   // useEffect(() => {
//   //   console.log("Fetching userDetails");
//   //   if (userToken) {
//   //     const userDetails = async () => {
//   //       try {
//   //         const response = await fetch("http://localhost:1514/prestoUserValidation",
//   //           {
//   //             method: "POST",
//   //             headers: {
//   //               "Content-Type": "application/json",
//   //             },
//   //             body: JSON.stringify({
//   //               userToken: "6yiy1A7LxAaCoYApUkZrrE8PqbQlZLfz",
//   //             }),
//   //           }
//   //         );
//   //         if (!response.ok) {
//   //           console.log("Network response was not ok");
//   //           // toast.error("Not a Valid Session", toastOptions);
//   //           setStatus(false);
//   //         } else {
//   //           const jsonData = await response.json();
//   //           console.log("jsonData: ", jsonData);

//   //           if (Array.isArray(jsonData) && jsonData.length === 0) {
//   //             setData(null); // If empty, set data to null
//   //             console.log("jsonData is empty");
//   //             // toast.error("Pass correct details/ Inactive User", toastOptions);
//   //           } else {
//   //             console.log("jsonData is not empty");
//   //             setStatus(true);
//   //             setData(jsonData); 
//   //             //pass the user details to login page by redirecting to login page
//   //           }
//   //         }
//   //       } catch (err) {
//   //         console.log(err);
//   //       }
//   //     };
//   //     userDetails();
//   //   }
//   // }, [userToken]);

//   useEffect(() => {
//     console.log("Fetching userDetails");
//     // Get the token from the query parameter in the URL
//     const urlParams = new URLSearchParams(window.location.search);
//     // const tokenFromURL = urlParams.get('token');
//     const tokenFromURL = '6yiy1A7LxAaCoYApUkZrrE8PqbQlZLfz';

//     if (tokenFromURL) {
//       setToken(tokenFromURL);

//       // Send the token to the Node.js server for validation
//       fetch(`http://localhost:1514/prestoUserValidation?token=${tokenFromURL}`){
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//           userDetails: userDetails,
//           message: input,
//           sessionId: sessionId,
//         }),
//       })
//         .then((response) => {
//           // {console.log("response: " + response.json())}
//           return new Promise((resolve) => {resolve(response.json());});
//         })
//         .then((data) => handleMessageResponse(data))

//         // .then(response => {
//         //   setIsValid(response.data.isValid);
//         // })
//         .catch(error => {
//           console.error('Error validating token:', error);
//         });
    
//   }, []);

//   return (
//     <div>
//       {" "}
//       PrestoPage
//       <div>Status: {status ? "Valid" : "Invalid"}</div>
//       <div>Data: {data ? JSON.stringify(data) : "No data"}</div>
//     </div>
//   );
// }

// export default PrestoPage;
