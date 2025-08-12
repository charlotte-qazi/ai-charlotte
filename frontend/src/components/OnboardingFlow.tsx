/*
 * AI Charlotte - Onboarding Flow Component
 * Copyright (c) 2025 Charlotte Qazi
 * 
 * This project is created and maintained by Charlotte Qazi.
 * For more information, visit: https://github.com/charlotteqazi
 * 
 * Licensed under the MIT License.
 */

import React, { useState, useEffect } from 'react'
import axios from 'axios'
import config from '../config'
import ChatContainer, { type ChatMessage } from './ChatContainer'

interface OnboardingFlowProps {
  onComplete: (userId: string, welcomeMessage: string, userName: string) => void
}

const questions = [
  "Hi there! ✨ I'm Charlotte's AI assistant. Before we dive into learning about her, I'd love to get to know you a bit! What's your name?",
  "Nice to meet you, {name}! 😊 What brings you here today? Are you exploring AI, curious about my work, testing out chatbots... or maybe it's Charlotte's mum checking in again? 👀"
]

const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState("")
  const [loading, setLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  
  // Store answers
  const [answers, setAnswers] = useState({
    name: '',
    interests: ''
  })

  // Start with first question
  useEffect(() => {
    const initialMessage: ChatMessage = {
      id: 1,
      role: 'assistant',
      content: questions[0],
      timestamp: new Date(),
    }
    setMessages([initialMessage])
  }, [])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: ChatMessage = {
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

    if (currentStep < 1) {
      // Show next question
      const nextStep = currentStep + 1
      setCurrentStep(nextStep)
      
      let nextQuestion = questions[nextStep]
      if (nextStep === 1) {
        nextQuestion = nextQuestion.replace('{name}', answer)
      }

      setTimeout(() => {
        const assistantMessage: ChatMessage = {
          id: messages.length + 2,
          role: 'assistant',
          content: nextQuestion,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, assistantMessage])
      }, 500)

    } else {
      // Complete onboarding
      setLoading(true)
      
      try {
        const finalAnswers = {
          name: currentStep === 0 ? answer : answers.name,
          interests: currentStep === 1 ? answer : answers.interests
        }

        const response = await axios.post(`${config.apiBaseUrl}/api/users`, finalAnswers)
        const { user_id } = response.data

        // Save user data to localStorage
        localStorage.setItem('user_id', user_id)
        localStorage.setItem('user_name', finalAnswers.name)

        // Generate welcome message
        const welcomeMessage = `Perfect! Thanks for sharing, ${finalAnswers.name}! 🎉 Now I'm all set to help you learn about Charlotte. You can ask me anything about her experience, projects, or interests. What would you like to know first?`

        // Show welcome message
        const welcomeMsg: ChatMessage = {
          id: messages.length + 2,
          role: 'assistant',
          content: welcomeMessage,
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, welcomeMsg])
        
        // Complete onboarding after a delay
        setTimeout(() => {
          onComplete(user_id, welcomeMessage, finalAnswers.name)
        }, 2000)

      } catch (error) {
        console.error('Error creating user:', error)
        const errorMessage: ChatMessage = {
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

  return (
    <ChatContainer
      messages={messages}
      inputValue={inputValue}
      onInputChange={setInputValue}
      onSendMessage={handleSendMessage}
      loading={loading}
      placeholder="Type your answer here... ✨"
      loadingText="Saving your information..."
    />
  )
}

export default OnboardingFlow 