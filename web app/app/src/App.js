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
  const urlParams = new URLSearchParams(window.location.search);
  
  let tokentoPrestoPage;
  tokentoPrestoPage = urlParams.get('token');
  
  useEffect(() => {
    const auth = localStorage.getItem("user");
    const userToken = localStorage.getItem("userToken");
    // const urlParams = new URLSearchParams(window.location.search);
    tokentoPrestoPage = urlParams.get('token');
    console.log("Entry 1 Token: ", tokentoPrestoPage);
    if (tokentoPrestoPage) {
      console.log("Entry 2 Token: ", tokentoPrestoPage);
      setIsUserToken(true);
      navigate(`/presto/${tokentoPrestoPage}`);
    }
    if(tokentoPrestoPage){
      setIsNavBar(false);
    }
    if (auth) {
      setIsLogin(true);
    }
  }, []);

  return (
    <Routes>
      <Route basename={process.env.PUBLIC_URL} />
      <Route path="/" element={<LoginPage />} />
      <Route path={process.env.PUBLIC_URL} element={<LoginPage />} />
      <Route path="/presto/:tokentoPrestoPage" element={<PrestoPage />} />
      <Route
        //path={process.env.REACT_APP_AI_REDIRECT}
        //run on localhost
         path="/aichat"
        element={
          <div className="App" style={{ display: "flex", height: "100vh" }}>
            {/* {isNavBar && <Navbar />} */}
            {/* <Navbar prestURL={isNavBar}/> */}
            {isNavBar && <Navbar prestURL={isNavBar}/>}
            <Sidebar className="sideCSS" visible={sideNavVisible} show={showSidebar}/>
            <div className={!sideNavVisible ? "page" : "page page-with-sidenavbar"}>
              <AIChat visible={sideNavVisible} prestURL={isNavBar}/>
              
              
            </div>
          </div>
        }
      /> 
    </Routes>
  );
}

export default App;
