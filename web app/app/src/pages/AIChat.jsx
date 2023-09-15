import React, { useState, useEffect, useRef } from "react";
import "../styles/aichat.css";
import ChatMessage from "../components/ChatMessage";
import { usePromiseTracker, trackPromise } from "react-promise-tracker";
import TextareaAutosize from 'react-textarea-autosize';
import LoadingSpinner from "../components/LoadingSpinner";
// import {useLocation} from "react-router-dom";
import {useNavigate } from "react-router-dom";
// import axios from "axios";
import jwt_decode from "jwt-decode";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMicrophone } from '@fortawesome/free-solid-svg-icons';
//import { faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { v4 as uuidv4 } from 'uuid';
// import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import * as sdk from 'microsoft-cognitiveservices-speech-sdk';
import { faMicrophoneLines } from "@fortawesome/free-solid-svg-icons";

const generateSessionId = () => {
  return uuidv4();
};

const AIChat = (props) => {
  // const location = useLocation();
  const navigate = useNavigate ();
  // const params = new URLSearchParams(location.search);
  // const userId = params.get('userId') || null;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  // const startListening = () => SpeechRecognition.startListening({ continuous: true, language: 'en-IN' });
  // const { transcript, browserSupportsSpeechRecognition , resetTranscript, listening} = useSpeechRecognition();

  const REACTAPP_CHATURL = process.env.REACT_APP_CHAT_URL;
  const REACT_APPHOST = process.env.REACT_APP_HOST;
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [timeoutId, setTimeoutId] = useState(null);
  const [isActive, setIsActive] = useState(false);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [user, setUser] = useState(null);
  const [input, setInput] = useState("");
  const [speechRecognitionLoading, setSpeechRecognitionLoading] = useState(false);
  const [micIcon, setIcon] = useState(faMicrophone);
  const [chatLog, setChatLog] = useState([
    {
      user: "gpt",
      message: "Hello, I am Kai. How can I help you?",
      metadata: "",
    },
  ]);
  
  const [selectedMessageIndex, setSelectedMessageIndex] = useState(-1);
  const inputRef = useRef(null);
  const { promiseInProgress } = usePromiseTracker();
  const messageEl = useRef(null);
  const [sessionId, setSessionId] = useState("");

    // Function to create and play a button click sound
    function playButtonClickSound() {
      // Create an AudioContext
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
   
      // Create an oscillator to generate a simple tone
      const oscillator = audioContext.createOscillator();
      oscillator.type = "sine"; // You can change the type of waveform
      oscillator.frequency.setValueAtTime(1000, audioContext.currentTime); // Adjust the frequency as needed
  
       // Connect the oscillator to the audio output
      oscillator.connect(audioContext.destination);
  
  
      // Start and stop the oscillator to create a short click sound
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.1); // Adjust the duration as needed
    }
  useEffect(() => {
    // Generate a new session ID on login or window refresh
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    // console.log('Generated Session ID:', sessionId);
  }, []);

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

  useEffect(() => {
    const authData = localStorage.getItem('auth');
    if (!authData) {
      navigate('/login'); // Replace '/login' with the actual login route
    } 
    else {
      const decodedToken = jwt_decode(JSON.parse(authData).auth);
      const currentDate = new Date();
      
      if (decodedToken.exp * 1000 < currentDate.getTime()) {
        console.log("use effect for authicate check");
        // Clear local storage and navigate to the login page
        localStorage.removeItem('auth');
        localStorage.removeItem('refreshToken');
        navigate('/login'); // Replace '/login' with the actual login route
      }
    }
  }, [input, navigate]);

  async function handleSubmit(e) {
    // Play button click sound
    
    let chatLogNew = [
      ...chatLog,
      { user: "me", message: `${input}`, metadata: "", chatType: 'newLine' },
    ];
    setInput("");
    setChatLog(chatLogNew);
    setSelectedMessageIndex(-1);
    

    //need to only send userid
    const token = JSON.parse(localStorage.getItem("auth"));
    const decodedToken = jwt_decode(token.auth);
    const userDetails = decodedToken.USER_ID;
    const refreshTokenlocal = JSON.parse(localStorage.getItem("refreshToken"));
    // console.log("token: " + token.auth);

    //grab all the coversations and send it to the backend (check if we can email the same)
    // const messages = chatLogNew.map((message) => message.message).join("\n");
    //**** this code is to pass the latest message check if needed any more else remove */

    const refreshToken = async () => {
      try {
        const res = await fetch("http://localhost:1514/refresh", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${refreshTokenlocal.refreshToken}`,
          },
        });
        const data = await res.json();
        // console.log("data acess token: " + data.accessToken);
        // console.log("data refresh token: " + data.refreshToken);
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
      const currentDate = new Date();
      if (decodedToken.exp * 1000 < currentDate.getTime()) {
        const data = await refreshToken();
        console.log("access token: " );
        console.log("refresh token: " );
        options.headers["Authorization"] = `Bearer ${data.refreshToken}`;
      }
      console.log(url);
      return fetch(url, options)
      .then((response) => {
        if (response.status === 403) {
          // Unauthorized access (authentication failure)
          localStorage.removeItem('auth'); // Clear authentication data
          localStorage.removeItem('refreshToken'); // Clear refresh token
          navigate('/login'); // Navigate to the login page
        }
        return response;
      })
      .catch((error) => {
        console.error("Error:", error);
        throw error;
      });
    };

    const handleMessageResponse = (data) => {
      console.log("data: " + JSON.stringify(data));
      let responseType ;
      if(data.message.summary)
        responseType = data.message.summary.type;
      const errorMessage = data.message.error_message;
      // console.log("responseType: " + responseType);

      let responseSummary;
      if(responseType === "line" || responseType === "bar" || responseType === "table" || responseType === "pie"){
        responseSummary = JSON.stringify(data.message.summary)
      } else if(data.message.error_message){
        responseSummary = errorMessage;
      }
      else responseSummary = data.message.summary;

      const responseMetadata = data.message.meta_data;

      if(responseType === "line" || responseType === "bar" || responseType === "table" || responseType === "pie"){
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
      //local testing URL
      fetch(REACTAPP_CHATURL, {
      // fetchWithTokenRefresh("http://localhost:1514/", {
      //dev testing URL/ RA
      // fetch("http://secure.pristineinfotech.com:4026/", {
      //Synthectic data testing URL
      // fetch("http://secure.pristineinfotech.com:1514/", {
      //C&S testing URL
      // fetch("http://secure.pristineinfotech.com:4028/", {
      //let response 
      //  fetch("https://secure1.pristineinfotech.com:1514/", {
        
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token.auth}`,
        },
        body: JSON.stringify({
          userDetails: userDetails,
          message: input,
          sessionId: sessionId,
        }),
      })
        .then((response) => {
          // {console.log("response: " + response.json())}
          return new Promise((resolve) => {resolve(response.json());});})
        .then((data) => handleMessageResponse(data)
  ))
}

const startListening = () => {
  console.log('startListening');
  const subscriptionKey = '42124f5a4bbd4b24946a867022a9b1c0';
  const serviceRegion = 'eastus';
  const speechConfig = sdk.SpeechConfig.fromSubscription(subscriptionKey, serviceRegion);
  speechConfig.speechRecognitionLanguage = 'en-US';
  speechConfig.outputFormat = sdk.OutputFormat.Detailed;
  speechConfig.enableDictation = true;
  speechConfig.continuous = true;
  const audioConfig = sdk.AudioConfig.fromDefaultMicrophoneInput();
  const recognizer = new sdk.SpeechRecognizer(speechConfig, audioConfig);
  recognizer.recognizeOnceAsync(result => {
    clearTimeout(timeoutId); // Clear the existing timeout.
    if (result.reason === sdk.ResultReason.RecognizedSpeech) {
      // Update the transcript state with the latest result
      setTranscript(result.text);
      setInput(result.text);
      // Set a new timeout to stop listening after 5 seconds of silence.
      setTimeoutId(setTimeout(() => {
        recognizer.stopContinuousRecognitionAsync();
        setListening(false);
        setIsActive(false);
        setSpeechRecognitionLoading(false);
        playButtonClickSound();
      }, 2000));
    } else if (result.reason === sdk.ResultReason.NoMatch) {
      // Handle no speech recognized or pause.
      console.log('No speech or pause.');
      startListening(); // Restart listening for speech.
    } else if (result.reason === sdk.ResultReason.Canceled) {
      const cancellation = sdk.CancellationDetails.fromResult(result);
      if (cancellation.reason === sdk.CancellationReason.Error) {
        console.error(`CANCELED: ErrorCode=${cancellation.errorCode}`);
        console.error(`CANCELED: ErrorDetails=${cancellation.errorDetails}`);
      }
    }
  });
  setListening(true);
};

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
  console.log('Speech recognition result.');
  const interimTranscript = event.results[event.results.length - 1][0].transcript;
  // console.log('Interim result:', interimTranscript);

  clearTimeout(recognitionTimeout); // Clear the timeout so we don't end up with multiple timeouts running at the same time
  // Check for a pause in the speech
  if (isChromeBrowser()) {
    recognitionTimeout = setTimeout(() => {
      console.log('No input detected for 100 mseconds. Stopping the recording.');
      recognition.stop();
      recognition.addEventListener("end", () => { console.log("Speech recognition service disconnected"); }); 
    }, 100);
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
  if (!isTyping) {
 
    setSpeechRecognitionLoading(true);
    setIcon(faMicrophone);

  // Play button click sound
  playButtonClickSound();
  
  console.log('handleIconClick', transcript);
  setTranscript('');
  setIsActive(true);
  startListening();
  
};
}

  return (
    <>
      <div className="chat-container">
        {/* <div className="chat-log" ref={messageEl}> */}
      <div className={!props.prestoURL ? 'chat-log' : 'chat-log-presto'} ref={messageEl}>  
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
             placeholder="Ask Kai" 
             value={listening ? transcript : input} onChange={handleChange}
             
             onKeyDown={(e) => {
              handleKeyDown(e);
              setIsTyping(true); // User started typing
            }}
            onKeyUp={() => {
              setIsTyping(false); // User stopped typing
            }}
            maxRows={5}
          />
             
          <button className={`microphone-icon ${isActive ? 'active' : ''}`}>
          {isActive && (
          <img
          src="https://media.giphy.com/media/sSgvbe1m3n93G/giphy.gif" // Updated URL
          alt="Microphone Animation"
          style={{ width: "30px", height: "30px" }} // Adjust the width and height as needed
              />
          )}
            <FontAwesomeIcon icon={isActive ? faMicrophoneLines : micIcon} onClick={handleIconClick} />
            </button>
          </div>
          <div className="flash-refresh send">
            <span className="send-span" onClick={handleSubmit}>
            
              
              <svg className="send-svg-container" xmlns="http://www.w3.org/2000/svg" viewBox="-3 -3 25 25" fill="none" 
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
