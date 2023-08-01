// chatRoutes.js
import express from 'express';
import chatbotController from '../controllers/chatbotController';

const express = require('express');
const router = express.Router();
const chatbotController = require('../controllers/chatbotController');

// Handle user messages
router.post('/user-message', chatbotController.handleUserMessage);

// Handle AI system responses
router.post('/ai-response', chatbotController.handleAIResponse);

module.exports = router;
