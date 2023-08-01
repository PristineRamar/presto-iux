import React, { useState, useEffect } from "react";
import TextField from '@mui/material/TextField';
import { useNavigate } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "../styles/login.css";


export default function Login() {
  const navigate = useNavigate();
  const [values, setValues] = useState({ username: "", password: "" });
  const [data, setData] = useState(null);
  const [status, setStatus] = useState(false);
  const toastOptions = { position: "bottom-right", autoClose: 8000, pauseOnHover: true, draggable: true,
    theme: "dark",
};

  useEffect(() => {
    const auth = localStorage.getItem('auth');
    if (auth) {
      navigate("/aichat");
    }
  });

  const handleChange = (event) => {
    setValues({ ...values, [event.target.name]: event.target.value });
  };

  const validateForm = () => {
    const { username, password } = values;
    if (username === "") {
      toast.error("Email and Password is required.", toastOptions);
      return false;
    } else if (password === "") {
      toast.error("Email and Password is required.", toastOptions);
      return false;
    }
    return true;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (validateForm()) {
      const { username, password } = values;
      console.log("username: " + username);
      console.log("password: " + password);
      // const { data } = await axios.post(loginRoute, {username, password,});

      let response = await fetch("http://localhost:1514/login", {
      // let response = await fetch("http://secure.pristineinfotech.com:1514/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    if (!response.ok) {
      console.log('Network response was not ok');
      toast.error("Retry again", toastOptions);
      setStatus(false);
    } else {
   
    const jsonData = await response.json();
    console.log("jsonData: ", jsonData);

    if (Array.isArray(jsonData) && jsonData.length === 0) {
      setData(null); // If empty, set data to null
      console.log('jsonData is empty');
      toast.error("Pass correct details/ Inactive User", toastOptions);
    } else {
      console.log('jsonData is not empty');
      setStatus(true);
      setData(jsonData); // Store the fetched data in the state
    }
  }
    
    }
  };

  // useEffect hook to log the updated value of status
  useEffect(() => {
    if (status === true) {

      console.log('status is true', data[0].USER_ID);
      localStorage.setItem("user",JSON.stringify(data[0]));
      localStorage.setItem("auth",JSON.stringify(data[1]));
      navigateToAiChat(data[0].USER_ID);
    }
  }, [data, status]);

  const navigateToAiChat = (userId) => {
    navigate(`/aichat?userId=${userId}`);
  };

  return (
    <>
      <div className="formatcont">
        <form action="" onSubmit={(event) => handleSubmit(event)}>
          <div className="brand"> <h1>Sign In</h1> </div>
          <TextField type="text" label="Username" placeholder="Username" name="username"
          onChange={(e) => handleChange(e)} variant="outlined" margin="normal" min="3"/>
          <TextField type="password" label="Password" placeholder="Password" name="password"
            onChange={(e) => handleChange(e)} variant="outlined" margin="normal" min="3"/>
          <button type="submit">Continue</button>
          {/* <span className="spanlogin"> Don't have an account ? <Link to="/register">Create One.</Link> </span> */}
        </form>
      </div>
      <ToastContainer />
    </>
  );
}