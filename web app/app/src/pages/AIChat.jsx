import React, { useState, useEffect, useRef } from "react";
import "../styles/aichat.css";
import ChatMessage from "../components/ChatMessage";
import { usePromiseTracker, trackPromise } from "react-promise-tracker";
import TextareaAutosize from 'react-textarea-autosize';
import LoadingSpinner from "../components/LoadingSpinner";
import {useLocation} from "react-router-dom";

const AIChat = (props) => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const userId = params.get('userId') || null;

  const [input, setInput] = useState("");
  const [chatLog, setChatLog] = useState([
    {
      user: "gpt",
      message: "Hello, I am Presto. How can I help you?",
      metadata: "",
    },
  ]);
  
  const [selectedMessageIndex, setSelectedMessageIndex] = useState(-1);
  const inputRef = useRef(null);
  const { promiseInProgress } = usePromiseTracker();
  const messageEl = useRef(null);
 

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    if (messageEl) {
      const observer = new MutationObserver(mutationsList => {
        // Handle the mutations
        mutationsList.forEach(mutation => {
          if (mutation.type === 'childList') {
            const { target } = mutation;
            target.scroll({ top: target.scrollHeight, behavior: 'smooth' });
          }
        });
      });

      // Observe the messageEl.current element
    observer.observe(messageEl.current, { childList: true });
    }

    // observer.disconnect();
  }, [])

  async function handleSubmit(e) {
    let chatLogNew = [
      ...chatLog,
      { user: "me", message: `${input}`, metadata: "", chatType: 'newLine' },
    ];
    setInput("");
    setChatLog(chatLogNew);
    setSelectedMessageIndex(-1);

    //need to only send userid
    const userDetails = userId;
    const token = JSON.parse(localStorage.getItem("auth"));

    //grab all the coversations and send it to the backend (check if we can email the same)
    // const messages = chatLogNew.map((message) => message.message).join("\n");
    //**** this code is to pass the latest message check if needed any more else remove */


    trackPromise(
      fetch("http://localhost:1514/", {
      // fetch("http://secure.pristineinfotech.com:1514/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token.auth}`,
        },
        body: JSON.stringify({
          userDetails: userDetails,
          message: input,
        }),
      })
        // .then((response) => {return new Promise((resolve) => {setTimeout(() => {resolve(response.json());}, 2000);});})
        .then((response) => {return new Promise((resolve) => {resolve(response.json());});})
        .then((data) => {
    // const data = await response.json();
    console.log("data type: " + data);

    const responseType = data.message.type;

    let responseSummary;
    if(responseType === "line" || responseType === "bar" || responseType === "table"){
      responseSummary = JSON.stringify(data.message.summary)
    } else responseSummary = data.message.summary;

    const responseMetadata = data.message.meta_data;
    
    // console.log("responseType: " + responseType);
    // console.log("responseSummary: " + responseSummary);

    if(responseType === "line" || responseType === "bar" || responseType === "table"){
      console.log("chatLog is a chart");
      setChatLog([...chatLogNew,
        {user: "gpt",message: `${responseSummary}`,metadata: responseMetadata,chatType: responseType,},]);
    }
    else if (Array.isArray(responseSummary)) {
      setChatLog([...chatLogNew,
        {user: "gpt",message: `${responseSummary.slice(0, 7)}`,metadata: responseMetadata,chatType: "array",},]);
    } else if (typeof responseSummary === "string") {
      const hasNewLine = responseSummary.includes("\n");
      setChatLog([...chatLogNew,
        {user: "gpt", message: `${responseSummary}`, metadata: responseMetadata, chatType: hasNewLine ? "newLine" : "string",},
      ]);
    } else {
      console.log("chatLog is neither an array nor a string");
    }
  }))
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
              visible={props.visible}
            />
          ))}
          {promiseInProgress && <LoadingSpinner />}
        </div>
        <div
          className={
            !props.visible
              ? "chat-input-holder"
              : "chat-input-holder-with-sidebar"
          }
        >
          <div className="flash-refresh">
            <span onClick={clearChat}>
              <div className="svg-container">
                <svg
                  viewBox="0 0 28 28"
                  aria-hidden="true"
                  fill="#1389fd"
                  width="25"
                  height="25"
                >
                  <path d="M12.747 16.273h-7.46L18.925 1.5l-3.671 10.227h7.46L9.075 26.5l3.671-10.227z"></path>
                </svg>
              </div>
            </span>
          </div>
          <div className="chat-input">
            <TextareaAutosize
              className="chat-input-textarea"
              style={{ width: "100%" }}
              placeholder="Ask Presto"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              maxRows={5}
            />
          </div>
          <div className="flash-refresh send">
            <span onClick={handleSubmit}>
              <svg
                className="send-svg-container"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="-4 -4 25 25"
                fill="none"
                class="h-4 w-4 m-1 md:m-0"
                stroke-width="2"
              >
                <path
                  d="M.5 1.163A1 1 0 0 1 1.97.28l12.868 6.837a1 1 0 0 1 0 1.766L1.969 15.72A1 1 0 0 1 .5 14.836V10.33a1 1 0 0 1 .816-.983L8.5 8 1.316 6.653A1 1 0 0 1 .5 5.67V1.163Z"
                  fill="currentColor"
                ></path>
              </svg>
            </span>
          </div>
        </div>
      </div>
    </>
  );
};

export default AIChat;
