import React, { useState, useEffect, useRef } from "react";
import "../styles/aichat.css";
import ChatMessage from "../components/ChatMessage";
import { usePromiseTracker, trackPromise } from "react-promise-tracker";
import TextareaAutosize from 'react-textarea-autosize';
import LoadingSpinner from "../components/LoadingSpinner";
import {useLocation} from "react-router-dom";
import axios from "axios";
import jwt_decode from "jwt-decode";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMicrophone } from '@fortawesome/free-solid-svg-icons';
// import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const AIChat = (props) => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const userId = params.get('userId') || null;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  // const startListening = () => SpeechRecognition.startListening({ continuous: true, language: 'en-IN' });
  // const { transcript, browserSupportsSpeechRecognition , resetTranscript, listening} = useSpeechRecognition();

  const [isRecording, setIsRecording] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [user, setUser] = useState(null);
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
    observer.observe(messageEl.current, { childList: true });
    }
  }, [])

  useEffect(() => {
    if(!listening && transcript !== ''){
      console.log("true")
      simulateEnterKey();
      setTranscript('');
    }
  }, [transcript, listening]);
  

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
    const refreshTokenlocal = JSON.parse(localStorage.getItem("refreshToken"));
    // console.log("token: " + token.auth);

    //grab all the coversations and send it to the backend (check if we can email the same)
    // const messages = chatLogNew.map((message) => message.message).join("\n");
    //**** this code is to pass the latest message check if needed any more else remove */

    const refreshToken = async () => {
      try {
        const res = await fetch("https://localhost:1514/refresh", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${refreshTokenlocal.refreshToken}`,
          },
        });
        const data = await res.json();
        console.log("data acess token: " + data.accessToken);
        console.log("data refresh token: " + data.refreshToken);
        setUser({
          ...user,
          accessToken: data.accessToken,
          refreshToken: data.refreshToken,
        });
        return data;
      } catch (err) {
        console.log(err);
      }
    };

    const fetchWithTokenRefresh = async (url, options) => {
      // url = url || "http://localhost:1514/refresh";
      const currentDate = new Date();
      const decodedToken = jwt_decode(token.auth);
      if (decodedToken.exp * 1000 < currentDate.getTime()) {
        const data = await refreshToken();
        console.log("access token: " + data.accessToken);
        console.log("refresh token: " + data.refreshToken);
        options.headers["Authorization"] = `Bearer ${data.refreshToken}`;
      }
      console.log(url);
      return fetch(url, options);
    };

    const handleMessageResponse = (data) => {
      const responseType = data.message.summary.type;
      console.log("responseType: " + responseType);

      let responseSummary;
      if(responseType === "line" || responseType === "bar" || responseType === "table"){
        responseSummary = JSON.stringify(data.message.summary)
      } else responseSummary = data.message.summary;

      const responseMetadata = data.message.meta_data;

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
    }

    trackPromise(
      fetchWithTokenRefresh("http://localhost:1514/", {
      // fetch("http://secure.pristineinfotech.com:1514/", {
      //  fetch("https://secure1.pristineinfotech.com:1514/", {
        
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
        .then((response) => {
          return new Promise((resolve) => {resolve(response.json());});})
        .then((data) => handleMessageResponse(data)
  ))
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

//   if (!browserSupportsSpeechRecognition) {
//     return null
// }

const handleChange = (e) => {
  // console.log('handleChange', e.target.value);
  setInput(e.target.value);
};

recognition.continuous = true;
recognition.lang = 'en-IN';
recognition.interimResults = true;

recognition.onstart = () => {
  setIsActive(true);
  setIsRecording(true);
  setListening(true);
  console.log('Speech recognition started.');
};

recognition.onend = () => {
  setIsActive(false);
  setIsRecording(false);
  setListening(false);
  console.log('Speech recognition ended.');
};

const simulateEnterKey = () => {
  console.log('Simulating enter key press.');
  const event = new KeyboardEvent('keydown', { key: 'Enter' });
    handleKeyDown(event);
}

function isChromeBrowser() {
  return /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
}

function isSafariBrowser() {
  return /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
}

let recognitionTimeout;
recognition.onresult = (event) => {
  // console.log('Speech recognition result.');
  const interimTranscript = event.results[event.results.length - 1][0].transcript;
  // console.log('Interim result:', interimTranscript);

  clearTimeout(recognitionTimeout); // Clear the timeout so we don't end up with multiple timeouts running at the same time
  // Check for a pause in the speech
  if (isChromeBrowser()) {
    recognitionTimeout = setTimeout(() => {
      console.log('No input detected for 600 mseconds. Stopping the recording.');
      recognition.stop();
      recognition.addEventListener("end", () => { console.log("Speech recognition service disconnected"); }); 
    }, 600);
  } 
  if (isSafariBrowser()){
    recognitionTimeout = setTimeout(() => {
      console.log('No input detected for 1000 mseconds. Stopping the recording.');
      recognition.stop();
      recognition.addEventListener("end", () => { console.log("Speech recognition service disconnected"); }); 
    }, 1000);
  }
  else {
    if (interimTranscript.endsWith('.') || interimTranscript.endsWith('?') || interimTranscript.endsWith('!')) {
        console.log('Detected a pause in the sentence. Stopping the recording.');
        setTranscript('');
        recognition.stop();
      }
  }

  // Update the transcript state with the latest result
  setTranscript(interimTranscript);
  setInput(interimTranscript);
};

const handleIconClick = () => {
  console.log('handleIconClick', transcript);
  setTranscript('');
  if (!isRecording && !isActive) {
    setIsActive(true); // Set the microphone as active when starting recording
    setIsRecording(true);
    setListening(true);
    recognition.start();
  } else {
    console.log('stop listening');
    setIsActive(false); // Set the microphone as inactive when stopping recording
    setIsRecording(false);
    setListening(false);
    recognition.stop();
  }
};

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
        <div className={!props.visible? "chat-input-holder": "chat-input-holder-with-sidebar"}>
          <div className="flash-refresh">
            <span onClick={clearChat}>
              <div className="svg-container">
                <svg viewBox="0 0 28 28" aria-hidden="true" fill="#1389fd" width="25" height="25">
                  <path d="M12.747 16.273h-7.46L18.925 1.5l-3.671 10.227h7.46L9.075 26.5l3.671-10.227z"></path> 
                </svg>
              </div>
            </span>
          </div>
          <div className="chat-input">
            <TextareaAutosize className="chat-input-textarea" style={{ width: "100%" }} 
             placeholder="Ask Presto" 
             value={listening ? transcript : input} onChange={handleChange}
             onKeyDown={handleKeyDown} maxRows={5}/>
            <button className={`microphone-icon ${isActive ? 'active' : ''}`}>
              <FontAwesomeIcon icon={faMicrophone}  onClick={handleIconClick}/>
            </button>
          </div>
          <div className="flash-refresh send">
            <span className="send-span" onClick={handleSubmit}>
              <svg className="send-svg-container" xmlns="http://www.w3.org/2000/svg" viewBox="-4 -4 30 30" fill="none" 
              // class="h-4 w-4 m-1 md:m-0" stroke-width="2"
              >
                <path d="M.5 1.163A1 1 0 0 1 1.97.28l12.868 6.837a1 1 0 0 1 0 1.766L1.969 15.72A1 1 0 0 1 .5 14.836V10.33a1 1 0 0 1 .816-.983L8.5 8 1.316 6.653A1 1 0 0 1 .5 5.67V1.163Z" fill="currentColor"></path>
              </svg>
            </span>
          </div>
        </div>
      </div>
    </>
  );
};

export default AIChat;
