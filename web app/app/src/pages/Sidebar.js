import React from 'react';
import {
	FaBars,
	FaPlus,
	FaMapPin
} from 'react-icons/fa';
import { NavLink } from "react-router-dom";
import "../styles/sidebar.css";

const ICON_SIZE = 20;
const handleReloadPage = () => {
	window.location.reload();
  };

function Sidebar({visible, show}) {

	return (
		<>
			<div className="mobile-side">
				<button
					className="mobile-side-btn"
					onClick={() => show(!visible)}>
					<FaBars size={24}  />
				</button>
			</div>
			<side className={!visible ? 'sidebar' : 'hide-sidebar'}>
				<button
					type="button"
					className="side-btn"
					onClick={() => show(!visible)}>
					{/* { !visible? <FaAngleRight size={30} /> : <FaAngleLeft size={30} />} */}
					<FaBars size={24}  />
				</button>
				<div>
					<div className="links side-top">
						{/* <button className="side-link"> + New Chat </button> */}
						<NavLink to="/aichat" className="side-link" onClick={handleReloadPage}>
							<FaPlus size={ICON_SIZE} />
							<span className='spanSidebar'>New Chat</span>
						</NavLink>
						<NavLink to="/aichatv2" className="side-link">
							{/* <FaMapPin size={ICON_SIZE} /> */}
							<span>AIChatv2</span>
						</NavLink>
					</div>
				</div>
			</side>
		</>
  );
}

export default Sidebar;
