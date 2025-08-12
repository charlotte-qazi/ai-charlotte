/*
 * AI Charlotte - Onboarding Flow Component
 * Copyright (c) 2025 Charlotte Qazi
 * 
 * This project is created and maintained by Charlotte Qazi.
 * For more information, visit: https://github.com/charlotteqazi
 * 
 * Licensed under the MIT License.
 */

import React, { useState, useEffect, useRef } from 'react'
import { 
  Box, 
  Paper, 
  Typography, 
  TextField, 
  IconButton, 
  Avatar, 
  CircularProgress 
} from '@mui/material'
import { Send as SendIcon, SupportAgent, Face3 } from '@mui/icons-material'
import axios from 'axios'

interface OnboardingMessage {
  id: number
  role: 'assistant' | 'user'
  content: string
  timestamp: Date
}

interface OnboardingFlowProps {
  onComplete: (userId: string, welcomeMessage: string) => void
}

const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete }) => {
  const [messages, setMessages] = useState<OnboardingMessage[]>([])
  const [inputValue, setInputValue] = useState("")
  const [loading, setLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  // Collect answers in state
  const [answers, setAnswers] = useState({
    name: '',
    interests: ''
  })

  const questions = [
    "Hi there! ✨ I'm Charlotte's AI assistant. Before we dive into learning about her, I'd love to get to know you a bit! What's your name?",
    "Nice to meet you, {name}! 😊 What brings you here today? Are you exploring AI, curious about my work, testing out chatbots... or maybe it's Charlotte's mum checking in again? 👀"
  ]

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatContainerRef.current) {
      const scrollElement = chatContainerRef.current
      requestAnimationFrame(() => {
        scrollElement.scrollTop = scrollElement.scrollHeight
      })
    }
  }, [messages])

  // Start with first question
  useEffect(() => {
    const initialMessage: OnboardingMessage = {
      id: 1,
      role: 'assistant',
      content: questions[0],
      timestamp: new Date(),
    }
    setMessages([initialMessage])
  }, [])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: OnboardingMessage = {
      id: messages.length + 1,
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const answer = inputValue.trim()
    setInputValue("")

    // Store the answer
    if (currentStep === 0) {
      setAnswers(prev => ({ ...prev, name: answer }))
    } else if (currentStep === 1) {
      setAnswers(prev => ({ ...prev, interests: answer }))
    }

    // Move to next step or complete
    if (currentStep < 1) {
      // Show next question
      const nextStep = currentStep + 1
      setCurrentStep(nextStep)
      
      let nextQuestion = questions[nextStep]
      if (nextStep === 1) {
        nextQuestion = nextQuestion.replace('{name}', answer)
      }

      setTimeout(() => {
        const assistantMessage: OnboardingMessage = {
          id: messages.length + 2,
          role: 'assistant',
          content: nextQuestion,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, assistantMessage])
      }, 500)

    } else {
      // Complete onboarding - make API call with all answers
      setLoading(true)
      
      try {
        const finalAnswers = {
          name: currentStep === 0 ? answer : answers.name,
          interests: currentStep === 1 ? answer : answers.interests
        }

        const response = await axios.post('/api/users', finalAnswers)
        const { user_id } = response.data

        // Generate welcome message in frontend
        const welcomeMessage = `Perfect! Thanks for sharing, ${finalAnswers.name}! 🎉 Now I'm all set to help you learn about Charlotte. You can ask me anything about her experience, projects, or interests. What would you like to know first?`

        // Show welcome message
        const welcomeMsg: OnboardingMessage = {
          id: messages.length + 2,
          role: 'assistant',
          content: welcomeMessage,
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, welcomeMsg])
        
        // Complete onboarding after showing message
        setTimeout(() => {
          onComplete(user_id, welcomeMessage)
        }, 2000)

      } catch (error) {
        console.error('Error creating user:', error)
        const errorMessage: OnboardingMessage = {
          id: messages.length + 2,
          role: 'assistant',
          content: 'Sorry, something went wrong saving your information. Please try again! 💔',
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, errorMessage])
      } finally {
        setLoading(false)
      }
    }
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Chat Messages - Same structure as main App */}
      <Box
        ref={chatContainerRef}
        sx={{
          flex: 1,
          overflowY: "auto",
          p: 3,
          display: "flex",
          flexDirection: "column",
          gap: 2,
        }}
      >
        {messages.map((message, index) => (
          <Box
            key={message.id}
            sx={{
              display: "flex",
              justifyContent: message.role === 'assistant' ? "flex-start" : "flex-end",
              alignItems: "flex-start",
              gap: 2,
              opacity: 1,
              animation: `fadeInUp 0.6s ease-out ${index * 0.1}s both`,
              "@keyframes fadeInUp": {
                "0%": {
                  opacity: 0,
                  transform: "translateY(20px)",
                },
                "100%": {
                  opacity: 1,
                  transform: "translateY(0)",
                },
              },
            }}
          >
            {message.role === 'assistant' && (
              <Avatar
                sx={{
                  bgcolor: "primary.main",
                  width: 36,
                  height: 36,
                  mt: 0.5,
                }}
              >
                <SupportAgent sx={{ fontSize: 30 }} />
              </Avatar>
            )}

            <Paper
              elevation={0}
              sx={{
                p: 2.5,
                maxWidth: "75%",
                bgcolor: message.role === 'assistant' ? "#f8f9fa" : "primary.main",
                color: message.role === 'assistant' ? "text.primary" : "white",
                borderRadius: 3,
                border: message.role === 'assistant' ? "1px solid #e9ecef" : "none",
                ...(message.role === 'assistant'
                  ? {
                      borderBottomLeftRadius: 8,
                    }
                  : {
                      borderBottomRightRadius: 8,
                    }),
              }}
            >
              <Typography variant="body1" sx={{ lineHeight: 1.5 }}>
                {message.content}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  display: "block",
                  mt: 1,
                  opacity: 0.7,
                  fontSize: "0.75rem",
                }}
              >
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </Typography>
            </Paper>

            {message.role === 'user' && (
              <Avatar
                sx={{
                  bgcolor: "primary.light",
                  color: "primary.main",
                  width: 36,
                  height: 36,
                  mt: 0.5,
                  fontWeight: 600,
                }}
              >
                <Face3 sx={{ fontSize: 30 }} />
              </Avatar>
            )}
          </Box>
        ))}
        
        {loading && (
          <Box
            sx={{
              display: "flex",
              justifyContent: "flex-start",
              alignItems: "flex-start",
              gap: 2,
            }}
          >
            <Avatar
              sx={{
                bgcolor: "primary.main",
                width: 36,
                height: 36,
                mt: 0.5,
              }}
            >
              <SupportAgent sx={{ fontSize: 30 }} />
            </Avatar>
            <Paper
              elevation={0}
              sx={{
                p: 2.5,
                bgcolor: "#f8f9fa",
                borderRadius: 3,
                border: "1px solid #e9ecef",
                borderBottomLeftRadius: 8,
                display: "flex",
                alignItems: "center",
                gap: 1,
              }}
            >
              <CircularProgress size={16} sx={{ color: "primary.main" }} />
              <Typography variant="body1" sx={{ color: "text.secondary" }}>
                Saving your information...
              </Typography>
            </Paper>
          </Box>
        )}
      </Box>

      {/* Input Area - Same structure as main App */}
      <Box
        sx={{
          p: 3,
          borderTop: "1px solid #e9ecef",
          background: "rgba(248, 249, 250, 0.5)",
        }}
      >
        <Box sx={{ display: "flex", gap: 2, alignItems: "flex-end" }}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your answer here... ✨"
            variant="outlined"
            disabled={loading}
            sx={{
              "& .MuiOutlinedInput-root": {
                borderRadius: 3,
                bgcolor: "white",
                "&:hover .MuiOutlinedInput-notchedOutline": {
                  borderColor: "primary.main",
                },
                "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                  borderColor: "primary.main",
                  borderWidth: 2,
                },
              },
            }}
          />
          <IconButton
            onClick={handleSendMessage}
            aria-label="Send message"
            disabled={!inputValue.trim() || loading}
            sx={{
              bgcolor: "primary.main",
              color: "white",
              width: 48,
              height: 48,
              "&:hover": {
                bgcolor: "primary.dark",
              },
              "&.Mui-disabled": {
                bgcolor: "#e9ecef",
                color: "#6c757d",
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  )
}

export default OnboardingFlow 