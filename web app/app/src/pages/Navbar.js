import { useRef } from "react";
import { FaBars, FaTimes } from "react-icons/fa";
import "../styles/navbar.css";
import { Link, useNavigate } from "react-router-dom";
import logo from '../assets/Images/Kai_Black_Red_2.0.png';

function Navbar({prestURL}) {
  console.log("prestURL: ", prestURL);
  const auth = localStorage.getItem("user");
 	const navRef = useRef();
  const navigate = useNavigate();

	const showNavbar = () => {
		navRef.current.classList.toggle(
			"responsive_nav"
		);
	};

  const logout = () => {
    localStorage.clear();
    navigate(process.env.PUBLIC_URL) 
    // run on localhost
    // navigate('/')
}

	return (
    <header>
      <h3 className="tittle">
      <img
          src={logo}
          alt="Kai"
          className="logo"
          width="30px"
          height="30px"
        /></h3>
      <button className="nav-btn" onClick={showNavbar}>
        <FaBars />
      </button>
      <nav ref={navRef}>
        <button className="nav-btn nav-close-btn" onClick={showNavbar}>
          <FaTimes />
        </button>
        <ul className="nav-right">
          {!prestURL ? null :(auth ? (
          <li><Link onClick={logout} to={process.env.PUBLIC_URL}>Logout{" ("} {JSON.parse(auth).FIRST_NAME} {" "} {JSON.parse(auth).LAST_NAME}{" )"}</Link></li>
          // run on localhost
          // <li><Link onClick={logout} to="/">Logout{" ("} {JSON.parse(auth).FIRST_NAME} {" "} {JSON.parse(auth).LAST_NAME}{" )"}</Link></li>
          ):(
          <li><Link to={process.env.PUBLIC_URL}>Login</Link></li>))}
          // run on localhost
           {/* <li><Link to="/">Login</Link></li>))} */}
        </ul>
      </nav>
    </header>
  );
}

export default Navbar;