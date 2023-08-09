import React, { useEffect, useState } from "react";
import Sidebar from "./pages/Sidebar";
import { Routes, Route, useNavigate } from "react-router-dom";
import "./styles/index.css";
import AIChat from "./pages/AIChat";
import Navbar from "./pages/Navbar";
import LoginPage from "./pages/Login";


function App() {
  const [sideNavVisible, showSidebar] = useState(false);
  const [isLogin, setIsLogin] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const auth = localStorage.getItem("user");
    console.log("auth: ", auth);
    if (auth) {
      setIsLogin(true);
    }
  }, []);

  useEffect(() => {
    console.log("isLogin: ", isLogin);
    if (!isLogin) {
      // Redirect to login page
      navigate('/login');
    }
  }, [isLogin]);


  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/login" element={<LoginPage />} />
      {console.log("isLogin: ", isLogin)}
      {/* {isLogin ?  */}
      <Route
        path="/aichat"
        element={
          <div className="App" style={{ display: "flex", height: "100vh" }}>
            <Navbar />
            <Sidebar className="sideCSS" visible={sideNavVisible} show={showSidebar}/>
            <div className={!sideNavVisible ? "page" : "page page-with-sidenavbar"}>
              {console.log("sideNavVisible: ", sideNavVisible)}
              <AIChat visible={sideNavVisible}/>
            </div>
          </div>
        }
      /> 
      {/* : navigate("/login")}  */}
    </Routes>

    // <React.Fragment>
    //   	<div className="App" style={{ display: "flex", height: "100vh"}}>
    // 		<Navbar/>
    // 		<Sidebar className="sideCSS" visible={ sideNavVisible } show={ showSidebar }/>
    // 		<Routes>
    // 			<Route path="/" element={<Navigate to="/aichat" />} />
    // 			<Route path='/aichat' element={
    // 				<div className={!sideNavVisible ? "page" : "page page-with-sidenavbar"}>
    // 					<AIChat/>
    // 				</div>
    // 			} />
    // 			{/* <Route path='/pins' element={
    // 				<div className={!sideNavVisible ? "page" : "page page-with-sidenavbar"}>
    // 					<h1>pins</h1>
    // 				</div>
    // 			}/> */}
    // 		</Routes>
    // 	</div>
    // </React.Fragment>
  );
}

export default App;
