const greetings = [
  "Hi there! How may I be of assistance to you today?",
  "Welcome! How can I help you with your inquiries?",
  "Greetings! What can I do to assist you on this fine day?",
  "Hello, how may I provide support or answer any questions for you?",
  "Good day! How can I be of service to you at this moment?",
  "Hey! What brings you here today? How can I assist you?",
  "Salutations! How may I help you achieve your goals?",
];

const getGreeting = () => {
  return greetings[Math.floor(Math.random() * greetings.length)];
};
