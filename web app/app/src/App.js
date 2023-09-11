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
  const [isNavBar, setIsNavBar] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const auth = localStorage.getItem("user");
    const userToken = localStorage.getItem("userToken");
    if(userToken){
      setIsNavBar(false);
    }
    // console.log("auth: ", auth);
    if (auth) {
      setIsLogin(true);
    }
  }, []);


  //This code is the culprit for login page flashing on refresh
  // useEffect(() => {
  //   console.log("isLogin: ", isLogin);
  //   if (!isLogin) {
  //     navigate('/login');
  //   }
  // }, [isLogin]);


  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/login" element={<LoginPage />} />
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
