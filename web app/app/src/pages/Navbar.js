import { useRef } from "react";
import { FaBars, FaTimes } from "react-icons/fa";
import "../styles/navbar.css";
import { Link, useNavigate } from "react-router-dom";
// import jwt from "jsonwebtoken";

function Navbar() {
  const auth = localStorage.getItem("user");
  // console.log(auth);
  // const decodedJwt = jwt.decode(auth);
  // console.log(decodedJwt);
	const navRef = useRef();
  const navigate = useNavigate();

	const showNavbar = () => {
		navRef.current.classList.toggle(
			"responsive_nav"
		);
	};

  const logout = () => {
    localStorage.clear();
    navigate('/login')
}

	return (
    <header>
      <h3 className="tittle">IUX</h3>
      <button className="nav-btn" onClick={showNavbar}>
        <FaBars />
      </button>
      <nav ref={navRef}>
        <button className="nav-btn nav-close-btn" onClick={showNavbar}>
          <FaTimes />
        </button>
        <ul className="nav-right">
          {auth ? (
          <li><Link onClick={logout} to="/login">Logout{" ("} {JSON.parse(auth).FIRST_NAME} {" "} {JSON.parse(auth).LAST_NAME}{" )"}</Link></li>
          ):(
          <li><Link to="/login">Login</Link></li>)}
        </ul>

      </nav>

    </header>
  );
}

export default Navbar;