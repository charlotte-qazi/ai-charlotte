/*
 * AI Charlotte - React Frontend
 * Copyright (c) 2025 Charlotte Qazi
 * 
 * This project is created and maintained by Charlotte Qazi.
 * For more information, visit: https://github.com/charlotteqazi
 * 
 * Licensed under the MIT License.
 */

"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Box, Container, SpeedDial, SpeedDialAction } from "@mui/material"
import { Menu as MenuIcon, Email as EmailIcon,
  LinkedIn as LinkedInIcon,
  GitHub as GitHubIcon,
  Article as MediumIcon,
  Person as PortfolioIcon } from "@mui/icons-material"
import { createTheme, ThemeProvider } from "@mui/material/styles"
import axios from 'axios'
import OnboardingFlow from './components/OnboardingFlow'
import ChatContainer, { type ChatMessage } from './components/ChatContainer'

// Custom theme with Charlotte's brand colors
const theme = createTheme({
  palette: {
    primary: {
      main: "#d7288b", // raspberry
      light: "#ffbed5", // candy
      contrastText: "#fff3f7", // white
    },
    secondary: {
      main: "#6b717e", // grey
    },
    background: {
      default: "#fff3f7", // white background
      paper: "#ffffff", // accessible white for cards
    },
    text: {
      primary: "#525660", // accessible grey
      secondary: "#6b717e", // grey
    },
  },
  typography: {
    fontFamily: '"Raleway", sans-serif',
    h4: {
      fontWeight: 600,
      letterSpacing: "-0.02em",
    },
    h6: {
      fontWeight: 500,
      letterSpacing: "-0.01em",
    },
    body1: {
      lineHeight: 1.6,
    },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: "0 8px 32px rgba(215, 40, 139, 0.08)",
        },
      },
    },
  },
})

const speedDialActions = [
  {
    icon: <EmailIcon />,
    name: "Email",
    action: () => window.open("mailto:charlotte.qazi@gmail.com", "_blank"),
  },
  {
    icon: <LinkedInIcon />,
    name: "LinkedIn",
    action: () => window.open("https://linkedin.com/in/charlotteqazi", "_blank"),
  },
  {
    icon: <GitHubIcon />,
    name: "GitHub",
    action: () => window.open("https://github.com/charlotte-qazi", "_blank"),
  },
  {
    icon: <MediumIcon />,
    name: "Medium",
    action: () => window.open("https://medium.com/@charlotteqazi", "_blank"),
  },
  {
    icon: <PortfolioIcon />,
    name: "Portfolio",
    action: () => window.open("https://charlottemdavies.co.uk", "_blank"),
  },
]

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState("")
  const [loading, setLoading] = useState(false)
  const [isOnboardingComplete, setIsOnboardingComplete] = useState(false)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [sessionId, setSessionId] = useState<string | null>(null) // Used in future stages
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [userName, setUserName] = useState<string>("")

  // Check for existing authentication on page load
  useEffect(() => {
    const storedUserId = localStorage.getItem('user_id')
    const storedUserName = localStorage.getItem('user_name')
    
    if (storedUserId && storedUserName) {
      setSessionId(storedUserId)
      setUserName(storedUserName)
      setIsOnboardingComplete(true)
      
      // Set welcome message for returning user
      const welcomeMessage = `Welcome back, ${storedUserName}! 🎉 I'm ready to help you learn more about Charlotte. What would you like to know?`
      const welcomeMsg: ChatMessage = {
        id: 1,
        role: 'assistant',
        content: welcomeMessage,
        timestamp: new Date(),
      }
      setMessages([welcomeMsg])
    }
  }, [])

  // Utility function to clear authentication data (for future logout functionality)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const clearAuthData = () => {
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_name')
    setSessionId(null)
    setUserName("")
    setIsOnboardingComplete(false)
    setMessages([])
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: ChatMessage = {
      id: messages.length + 1,
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const messageContent = inputValue.trim()
    setInputValue("")
    setLoading(true)

    try {
      const resp = await axios.post('/api/chat', { message: messageContent })
      const answer: string = resp.data.answer
      
      const assistantMessage: ChatMessage = {
        id: messages.length + 2,
        role: 'assistant',
        content: answer,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: unknown) {
      console.error('Chat error:', error)
      const errorMessage: ChatMessage = {
        id: messages.length + 2,
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again! 💔',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleOnboardingComplete = (userId: string, welcomeMessage: string, userName: string) => {
    setSessionId(userId) // Store user ID for future use
    setUserName(userName) // Store user name
    setIsOnboardingComplete(true)
    
    // Add welcome message to chat
    const welcomeMsg: ChatMessage = {
      id: 1,
      role: 'assistant',
      content: welcomeMessage,
      timestamp: new Date(),
    }
    setMessages([welcomeMsg])
    
    // Save to localStorage (already done in OnboardingFlow, but ensuring consistency)
    localStorage.setItem('user_id', userId)
    localStorage.setItem('user_name', userName)
  }

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          height: "100vh",
          background: "linear-gradient(135deg, #fff3f7 0%, #ffbed5 100%)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Container 
          maxWidth="md" 
          sx={{ 
            flex: 1, 
            display: "flex", 
            flexDirection: "column",
            p: 2,
            boxSizing: "border-box",
            height: "100vh",
          }}
        >
          {!isOnboardingComplete ? (
            <OnboardingFlow onComplete={handleOnboardingComplete} />
          ) : (
            <ChatContainer
              messages={messages}
              inputValue={inputValue}
              onInputChange={setInputValue}
              onSendMessage={handleSendMessage}
              loading={loading}
              placeholder="Ask me anything about Charlotte's experience, projects, or interests... ✨"
              loadingText="Thinking..."
            />
          )}
        </Container>

        {/* SpeedDial - Fixed to bottom right, outside main layout */}
        <SpeedDial
          ariaLabel="Social Links"
          sx={{
            position: "fixed",
            bottom: 16,
            right: 16,
            zIndex: 1000,
            "& .MuiSpeedDial-fab": {
              bgcolor: "primary.main",
              color: "white",
              "&:hover": {
                bgcolor: "primary.dark",
              },
            },
          }}
          icon={<MenuIcon />}
        >
          {speedDialActions.map((action) => (
            <SpeedDialAction
              key={action.name}
              icon={action.icon}
              tooltipTitle={action.name}
              onClick={action.action}
              sx={{
                "& .MuiSpeedDialAction-fab": {
                  bgcolor: "background.paper",
                  color: "primary.main",
                  border: "2px solid",
                  borderColor: "primary.main",
                  "&:hover": {
                    bgcolor: "primary.main",
                    color: "white",
                  },
                },
              }}
            />
          ))}
        </SpeedDial>
      </Box>
    </ThemeProvider>
  )
}

export default App
