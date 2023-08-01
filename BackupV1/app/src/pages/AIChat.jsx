import React, { useState, useEffect, useRef } from "react";
import "../style/AIChat.css";
import ChatMessage from "../components/ChatMessage";
import { usePromiseTracker, trackPromise } from "react-promise-tracker";
import TextareaAutosize from '@material-ui/core/TextareaAutosize';
import LoadingSpinner from "../components/LoadingSpinner";
import IconButton from '@material-ui/core/IconButton';
import SendIcon from '@material-ui/icons/Send';
import InputAdornment from '@material-ui/core/InputAdornment';

const Transactions = () => {
  const [input, setInput] = useState("");
  const [chatLog, setChatLog] = useState([
    {
      user: "gpt",
      message: "Hello, I am Presto. How can I help you?",
      metadata: "",
    },
  ]);
  // const [chatType, setChatType] = useState("string");
  // const [summary, setSummary] = useState("");
  // const [metadata, setMetadata] = useState({});
  const [selectedMessageIndex, setSelectedMessageIndex] = useState(-1);
  const inputRef = useRef(null);
  const { promiseInProgress } = usePromiseTracker();
  // const [loading, setLoading] = useState(false);
  const messageEl = useRef(null);


  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    if (messageEl) {
      messageEl.current.addEventListener('DOMNodeInserted', event => {
        const { currentTarget: target } = event;
        target.scroll({ top: target.scrollHeight, behavior: 'smooth' });
      });
    }
  }, [])

  async function handleSubmit(e) {
    // e.preventDefault();
    // setLoading(true);
    let chatLogNew = [
      ...chatLog,
      { user: "me", message: `${input}`, metadata: "", chatType: 'newLine' },
    ];
    setInput("");
    setChatLog(chatLogNew);
    setSelectedMessageIndex(-1);

    //need to only send userid
    const userDetails = { id: "123456" };
    //grab all the coversations and send it to the backend (check if we can email the same)
    // const messages = chatLogNew.map((message) => message.message).join("\n");
    //**** this code is to pass the latest message check if needed any more else remove */
    // const latestMessage = chatLogNew[chatLogNew.length - 1];
    // const latestMessageString = latestMessage.message;

    // const response = await fetch("http://localhost:1514/", {
    //   // const response = await fetch("http://secure.pristineinfotech.com:1514/", {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json",
    //   },
    //   body: JSON.stringify({
    //     userDetails: userDetails,
    //     message: latestMessageString,
    //   }),
    // });

    trackPromise(
      fetch("http://localhost:1514/", {
          // fetch("http://secure.pristineinfotech.com:1514/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userDetails: userDetails,
          message: input,
        }),
      })
        // .then((response) => response.json())
        .then((response) => {return new Promise((resolve) => {setTimeout(() => {resolve(response.json());}, 2000);});})
        .then((data) => {
    // const data = await response.json();
    // console.log("data: " + data);
    const responseSummary = data.message.summary;
    const responseMetadata = data.message.meta_data;

    // setSummary(responseSummary);
    // setMetadata(responseMetadata);

    //for chart and table check if the response is json response and based on the type call the handler
    if (Array.isArray(responseSummary)) {
      console.log("chatLog is an array");
      // setChatType("array");
      setChatLog([...chatLogNew,{user: "gpt",message: `${responseSummary.slice(0, 7)}`,metadata: responseMetadata,chatType: "array",},]);
    } else if (typeof responseSummary === "string") {
      console.log("chatLog is a string");
      const hasNewLine = responseSummary.includes("\n");
      // if (hasNewLine) {setChatType("newLine");}
      // else {setChatType("string");}
      // setChatType(false);
      setChatLog([...chatLogNew,
        {user: "gpt", message: `${responseSummary}`, metadata: responseMetadata, chatType: hasNewLine ? "newLine" : "string",},
      ]);
    } else {
      console.log("chatLog is neither an array nor a string");
    }
  }))

  // setLoading(false);
}

  function clearChat() {
    setChatLog([]);
  }


  function handleKeyDown(e) {
    if (e.key === "ArrowUp") {
      e.preventDefault();
      if (selectedMessageIndex < chatLog.length - 1) {
        setSelectedMessageIndex((prevIndex) => prevIndex + 1);
        setInput(chatLog[chatLog.length - 1 - selectedMessageIndex - 1].message);
      }
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (selectedMessageIndex >= 0) {
        setSelectedMessageIndex((prevIndex) => prevIndex - 1);
        setInput(chatLog[chatLog.length - 1 - selectedMessageIndex - 1].message);
      }
    } else if (e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <>
      <div className="chat-container">
        <div className="chat-log" ref={messageEl}>
          {chatLog.map((message, index) => (
            <ChatMessage
              key={index}
              message={message}
              metadata={message.metadata}
              chatType={message.chatType}
            />
          ))}
          {promiseInProgress && (
            <LoadingSpinner />
          )}
        </div>
        <div className="chat-input-holder">
          <div className="flash-refresh">
            <span onClick={clearChat}>
              <div className="svg-container">
                <svg
                  viewBox="0 0 28 28"
                  aria-hidden="true"
                  fill="#1389fd"
                  width="28"
                  height="28"
                >
                  <path d="M12.747 16.273h-7.46L18.925 1.5l-3.671 10.227h7.46L9.075 26.5l3.671-10.227z"></path>
                </svg>
              </div>
            </span>
          </div>
          <div className="chat-input">
            {/* <form onSubmit={handleSubmit}>
              <input
                rows="1"
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                className="chat-input-textarea"
                placeholder="Ask Presto"
                style={{ 
                  width: `100%` ,
                  // width: `${input.length * 8}px`,
                  rows: Math.min(5, input.split('\n').length), }}
              ></input>
            </form> */}
            <TextareaAutosize className="chat-input-textarea" style={{width: '100%'}} 
            placeholder="Ask Presto" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            maxRows={5}
            endAdornment={
              <InputAdornment position="end">
                <IconButton onClick={handleSubmit}>
                  <SendIcon />
                </IconButton>
              </InputAdornment>
            }/>
            
          </div>
          <div className="flash-refresh send">
            <span onClick={handleSubmit}>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 44">
                <defs>
                  <linearGradient
                    id="linear-gradient"
                    x1="0.208"
                    y1="0.796"
                    x2="0.682"
                    y2="0.277"
                    gradientUnits="objectBoundingBox"
                  >
                    <stop offset="0" stop-color="#1baff8" />
                    <stop offset="1" stop-color="#0f56b5" />
                  </linearGradient>
                </defs>
                <g
                  id="Group_177992"
                  data-name="Group 177992"
                  transform="translate(3734.914 5246.316)"
                >
                  <path
                    id="Path_91765"
                    data-name="Path 91765"
                    d="M22,.5a22,22,0,1,1-22,22A22,22,0,0,1,22,.5"
                    transform="translate(-3734.914 -5246.815)"
                    fill="#f6f6f7"
                  />
                  <path
                    id="Path_91768"
                    data-name="Path 91768"
                    d="M75.058,55.109,55.066,42.457a.821.821,0,0,0-1.209.5,1.414,1.414,0,0,0-.072.778l2.407,11.245H66.473v2.3H56.191l-2.449,11.2a1.217,1.217,0,0,0,.679,1.417.753.753,0,0,0,.638-.093l20-12.652a1.31,1.31,0,0,0,.394-1.548,1.063,1.063,0,0,0-.394-.5Z"
                    transform="translate(-3774.74 -5280.657)"
                    fill="url(#linear-gradient)"
                  />
                </g>
              </svg>
            </span>
          </div>
        </div>
      </div>
    </>
  );
};

export default Transactions;
