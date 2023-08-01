import React from "react";
import {ThreeDots} from 'react-loader-spinner';

const LoadingSpinner = () => {
  
  return (
    <div className="loader"
              style={{
                width: "100%",
                height: "100",
                display: "flex",
                justifyContent: "left",
                alignItems: "left",
              }}
            >
              <ThreeDots
                height="40"
                width="40"
                radius="9"
                color="#1BAFF8"
                ariaLabel="three-dots-loading"
                wrapperStyle={{}}
                wrapperClassName=""
                visible={true}
              />
            </div>
    );
};

export default LoadingSpinner;
