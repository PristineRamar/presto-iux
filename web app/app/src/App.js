import React, { useEffect, useState } from "react";
import Sidebar from "./pages/Sidebar";
import { Routes, Route, useNavigate } from "react-router-dom";
import "./styles/index.css";
import AIChat from "./pages/AIChat";
import Navbar from "./pages/Navbar";
import LoginPage from "./pages/Login";
import PrestoPage from "./pages/PrestoPage";


function App() {
  const [sideNavVisible, showSidebar] = useState(false);
  const [isLogin, setIsLogin] = useState(false);
  const [isUserToken, setIsUserToken] = useState(false);
  const [isNavBar, setIsNavBar] = useState(true);
  const navigate = useNavigate();

  let tokenFromURL;
  
  useEffect(() => {
    const auth = localStorage.getItem("user");
    const userToken = localStorage.getItem("userToken");
    const urlParams = new URLSearchParams(window.location.search);
    tokenFromURL = urlParams.get('token');
    console.log("tokenFromURL: ", tokenFromURL);
    if(userToken){
      setIsNavBar(false);
    }
    if (auth) {
      setIsLogin(true);
    }
    if (tokenFromURL) {
      setIsUserToken(true);
    }
  }, []);

  useEffect(() => {
    if (isUserToken) {
        navigate('/presto', {tokenFromURL});
    }
  }, [isUserToken]);

  // This code is the culprit for login page flashing on refresh
  useEffect(() => {
    console.log("isLogin: ", isLogin);
    console.log("isUserToken: ", isUserToken);
    // if (!isLogin && !isUserToken) {
    if (!isLogin) {
      console.log("isUserToken: ", isUserToken);
      console.log("Entry: ", isLogin);
      navigate('/KAIProd');
    }
  }, [isLogin]);



  return (
    <Routes>
      <Route basename={process.env.PUBLIC_URL} />
      <Route path="/" element={<LoginPage />} />
      <Route path="/KAIProd" element={<LoginPage />} />
      <Route path="/presto" element={<PrestoPage />} />
      {/* {console.log("isLogin: ", isLogin)} */}
      <Route
        path="/aichat"
        element={
          <div className="App" style={{ display: "flex", height: "100vh" }}>
            {/* {isNavBar && <Navbar />} */}
            <Navbar />
            <Sidebar className="sideCSS" visible={sideNavVisible} show={showSidebar}/>
            <div className={!sideNavVisible ? "page" : "page page-with-sidenavbar"}>
              {/* {console.log("sideNavVisible: ", sideNavVisible)} */}
              <AIChat visible={sideNavVisible}/>
            </div>
          </div>
        }
      /> 
    </Routes>
  );
}

export default App;
