const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const chatBody = document.getElementById("chat-body");
// const exportButton = document.getElementById("export-button");
// const refreshButton = document.getElementById("refresh-button");
let conversationUID = null;

const addTypingIndicator = () => {
  let typingIndicator = document.createElement("div");
  typingIndicator.id = "typing-indicator";
  typingIndicator.innerHTML =
    '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
  // add indicator to chat body
  chatBody.appendChild(typingIndicator);
};

const sendMessage = () => {
  let messageText = messageInput.value.trim();
  if (messageText !== "") {
    addMessage(messageText, "outgoing");
    messageInput.value = "";
    // create typing indicator
    addTypingIndicator();
    // build message object
    let msgObject = { message: messageText, cid: conversationUID };
    console.log(msgObject);
    // ajax POST request to chat server
    $.ajax({
      url: "/generate",
      type: "POST",
      data: JSON.stringify(msgObject),
      dataType: "json",
      contentType: "application/json; charset=utf-8",
      success: function (data) {
        console.log(data);
        // add to chat body after getting response
        respondToUser(data.message.trim());
      },
    });
  }
};

const removeElementById = (id) => {
  let elem = document.getElementById(id);
  if (elem) {
    elem.remove();
  }
};

const addCode = (codeContent, messageElementId = null) => {
  let messageElement = null;
  if (messageElementId == null) {
    messageElement = document.createElement("div");
    messageElement.id = generateUUID();
    messageElement.classList.add("chat-message");
    messageElement.classList.add("incoming");
    messageElement.setAttribute(
      "style",
      "width:400px !important; background-color:#F4F5FC !important"
    );
    // add message element to chat body
    chatBody.appendChild(messageElement);
  } else {
    messageElement = document.getElementById(messageElementId);
    let codeContainerElement =
      messageElement.getElementsByClassName("code-container");
    if (codeContainerElement != null) {
      codeContainerElement[0].remove();
    }
  }
  // create code container
  let codeContainer = document.createElement("div");
  codeContainer.classList.add("code-container");
  // highlight code
  let highlightedCode = highlightPythonCode(codeContent);
  // remove existing like/dislike buttons
  removeElementById("like-button");
  removeElementById("dislike-button");
  // create like/dislike buttons
  let buttonDiv = document.createElement("div");
  buttonDiv.innerHTML = `<button id="dislike-button"><i class="fa fa-thumbs-down"></i></button><button id="like-button"><i class="fa fa-thumbs-up"></i></button>`;
  // add code to inner html of code container
  codeContainer.innerHTML = highlightedCode;
  // add code container to chat message
  messageElement.appendChild(codeContainer);
  // add buttonDiv to chat body
  messageElement.appendChild(buttonDiv);
  // add listeners to reaction buttons
  addListenersToReactionButtons();
  // Make code editable
  messageElement.addEventListener("click", function () {
    showEditPopup(messageElement);
  });
};

const sendFeedback = (reaction) => {
  // add feedback message to chat body
  addMessage("Feedback in progress ...", "incoming", true);
  addTypingIndicator();
  let feedbackObj = {
    data: getMessages(),
    cid: conversationUID,
    useForTraining: reaction,
    timestamp: new Date().toString(),
  };
  console.log(feedbackObj);
  $.ajax({
    url: "/feedback",
    type: "POST",
    data: JSON.stringify(feedbackObj),
    dataType: "json",
    contentType: "application/json; charset=utf-8",
    success: function (data) {
      console.log(data);
      // remove typing indicator
      document.getElementById("typing-indicator").remove();
      // clear messages
      removeElementsByClass("chat-message");
      // add greetings!
      addMessage(getGreeting(), "incoming");
      // set new conversation id
      conversationUID = generateUUID();
    },
  });
};

const likeAction = () => {
  console.log("Like");
  sendFeedback("yes");
};
const dislikeAction = () => {
  console.log("Dislike");
  sendFeedback("no");
};

const addListenersToReactionButtons = () => {
  let likeButton = document.getElementById("like-button");
  let dislikeButton = document.getElementById("dislike-button");
  likeButton.addEventListener("click", likeAction);
  dislikeButton.addEventListener("click", dislikeAction);
};

const respondToUser = (msg) => {
  // first remove the typing indicator
  document.getElementById("typing-indicator").remove();
  // create a response message
  if (msg.includes("=") && msg.includes("(") && msg.includes(")")) {
    addCode(msg);
  } else {
    addMessage(msg, "incoming");
  }
};

const addMessage = (messsageContent, messageDirection, doNotLog = false) => {
  let messageElement = document.createElement("div");
  messageElement.id = generateUUID();
  messageElement.classList.add("chat-message");
  if (doNotLog) {
    messageElement.classList.add("do-not-log");
  }
  messageElement.classList.add(messageDirection);
  messageElement.innerHTML = `<p>${messsageContent}</p>`;
  chatBody.appendChild(messageElement);
  // add editable popup listener
  messageElement.addEventListener("click", function () {
    showEditPopup(messageElement);
  });
};

const getMessages = () => {
  let parent = document.getElementById("chat-body");
  let children = parent.children;
  let messages = [];
  for (var i = 0; i < children.length; i++) {
    var messageElement = children[i];
    // do not log system messages
    if (
      messageElement == null ||
      messageElement.classList.contains("do-not-log") ||
      messageElement.textContent.trim().length == 0
    ) {
      continue;
    }

    var messageDirection = messageElement.classList[1];
    messages.push({
      message: messageElement.textContent.trim(),
      utteranceIndex: i,
      role: messageDirection == "outgoing" ? "User" : "AI",
    });
  }
  return messages;
};

const exportMessages = () => {
  // get messages from chat box
  let messages = getMessages();
  // add exporting message to chat body
  addMessage("Export in progress ...", "incoming", true);
  addTypingIndicator();
  // add timestamp to export payload
  let exportObj = {
    data: messages,
    timestamp: new Date().toString(),
    cid: conversationUID,
  };
  // ajax POST request to chat server with list of messages as payload
  $.ajax({
    url: "/export",
    type: "POST",
    data: JSON.stringify(exportObj),
    dataType: "json",
    contentType: "application/json; charset=utf-8",
    success: function (data) {
      console.log(data);
      // remove typing indicator
      document.getElementById("typing-indicator").remove();
      // clear messages
      removeElementsByClass("chat-message");
      // add greetings!
      addMessage(getGreeting(), "incoming");
      // set new conversation id
      conversationUID = generateUUID();
    },
  });
};

const triggerModelUpdate = () => {
  // add exporting message to chat body
  addMessage("Triggering model update ...", "incoming");
  addTypingIndicator();

  // ajax GET request to chat server with list of messages as payload
  $.ajax({
    url: "/update-model",
    type: "GET",
    dataType: "json",
    contentType: "application/json; charset=utf-8",
    success: function (data) {
      console.log(data);
      // remove typing indicator
      document.getElementById("typing-indicator").remove();
      // clear messages
      removeElementsByClass("chat-message");
    },
  });
};

const getConversationById = async (cid) => {
  // add loading message to chat body
  addMessage("Loading conversations. Please wait ...", "incoming");
  addTypingIndicator();

  try {
    const response = await fetch(`/getchat?cid=${cid}`);
    if (!response.ok) {
      throw new Error("Failed to fetch conversation!");
    }
    const data = await response.json();
    // remove typing indicator
    document.getElementById("typing-indicator").remove();
    return data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

function removeElementsByClass(className) {
  const elements = document.getElementsByClassName(className);
  while (elements.length > 0) {
    elements[0].parentNode.removeChild(elements[0]);
  }
}

const showEditPopup = (messageElement) => {
  const originalMessage = messageElement.textContent.trim();
  let updatedMessage = prompt(
    "Edit the message as you see fit.",
    originalMessage
  );
  // update message element
  if (
    updatedMessage != null &&
    updatedMessage.trim().length > 0 &&
    updatedMessage.trim() !== originalMessage
  ) {
    if (isCode(updatedMessage)) {
      addCode(updatedMessage, messageElement.id);
    } else {
      messageElement.innerHTML = "<p>" + updatedMessage + "</p>";
    }
  }
};

const isCode = (messageContent) =>
  messageContent.toLowerCase().includes("=") &&
  messageContent.toLowerCase().includes("(") &&
  messageContent.toLowerCase().includes(")");

const renderConversation = (messages, cid) => {
  if (cid == undefined) {
    return;
  }

  if (cid.trim().length == 0) {
    return;
  }

  console.log(messages, cid);
  // if (messages == null) {
  //   messages = getConversationById();
  // }
  conversationUID = cid;
  // clear existing conversation
  removeElementsByClass("chat-message");
  // iterate through messages
  messages.forEach((message) => {
    let messageDirection = message.role == "User" ? "outgoing" : "incoming";
    let messageContent = message.textContent.trim();
    if (isCode(messageContent)) {
      addCode(messageContent);
    } else {
      addMessage(messageContent, messageDirection);
    }
  });
};

// Create greeting
addMessage(getGreeting(), "incoming");
// set unique conversation id
conversationUID = generateUUID();

// Add onclick listener to each chat message
let chatMessages = document.getElementsByClassName("chat-message");
Array.from(chatMessages).forEach(function (message) {
  message.addEventListener("click", function () {
    showEditPopup(message);
  });
});

sendButton.addEventListener("click", sendMessage);
messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    sendMessage();
  }
});
// // add listener to export button
// exportButton.addEventListener("click", exportMessages);

// // add listener to refresh button
// refreshButton.addEventListener("click", triggerModelUpdate);
