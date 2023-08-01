// chatbotController.js
import aiSystemService from '../services/aiSystemService';
import chatbotService from '../services/chatbotService';


// Example controller functions

// Handle user messages
exports.handleUserMessage = (req, res) => {
    const userMessage = req.body.message;
  
    // Perform any necessary preprocessing on the user message
  
    // Forward the user message to the AI system and handle the response
    aiSystemService.sendMessage(userMessage)
      .then(aiResponse => {
        // Handle the AI system response
        // ...
  
        res.status(200).json({ response: aiResponse });
      })
      .catch(error => {
        // Handle any errors that occurred during AI system communication
        // ...
  
        res.status(500).json({ error: 'Internal Server Error' });
      });
  };
  
  // Handle AI system responses
  exports.handleAIResponse = (req, res) => {
    const aiResponse = req.body.response;
  
    // Perform any necessary preprocessing on the AI system response
  
    // Send the AI system response back to the chatbot
    chatbotService.sendMessage(aiResponse)
      .then(() => {
        res.status(200).json({ success: true });
      })
      .catch(error => {
        // Handle any errors that occurred during chatbot communication
        // ...
  
        res.status(500).json({ error: 'Internal Server Error' });
      });
  };
  