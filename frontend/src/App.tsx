"use client"

import type React from "react"
import { useState, useEffect, useRef } from "react"
import { Box, Paper, Typography, TextField, IconButton, Avatar, Container, Fade, CircularProgress } from "@mui/material"
import { Face3, Send as SendIcon, SupportAgent } from "@mui/icons-material"
import { createTheme, ThemeProvider } from "@mui/material/styles"
import axios from 'axios'

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

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: 'assistant',
      content: "Hi there! ✨ I'm Charlotte's AI assistant, here to help you learn more about her experience, projects, and personality. What would you like to know?",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [loading, setLoading] = useState(false)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (chatContainerRef.current) {
      const scrollElement = chatContainerRef.current
      // Use requestAnimationFrame to ensure DOM is updated
      requestAnimationFrame(() => {
        scrollElement.scrollTop = scrollElement.scrollHeight
      })
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: messages.length + 1,
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setLoading(true)

    try {
      const resp = await axios.post('/api/chat', { message: inputValue.trim() })
      const answer: string = resp.data.answer
      
      const assistantMessage: Message = {
        id: messages.length + 2,
        role: 'assistant',
        content: answer,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (e: any) {
      const errorMessage: Message = {
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

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          minHeight: "100vh",
          background: "linear-gradient(135deg, #fff3f7 0%, #ffbed5 100%)",
          py: 4,
        }}
      >
        <Container maxWidth="md">
          <Fade in timeout={800}>
            <Paper
              elevation={0}
              sx={{
                borderRadius: 4,
                overflow: "hidden",
                background: "rgba(255, 255, 255, 0.95)",
                backdropFilter: "blur(10px)",
              }}
            >
              {/* Header */}
              <Box
                sx={{
                  background: "linear-gradient(135deg, #d7288b 0%, #ffbed5 100%)",
                  p: 4,
                  textAlign: "center",
                  color: "white",
                }}
              >
                <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                  💁‍♀️ Meet AI-Charlotte
                </Typography>
                <Typography variant="body1" sx={{ opacity: 0.9, maxWidth: 600, mx: "auto" }}>
                  Your friendly guide to learning about Charlotte Qazi - software engineer, problem-solver, and creative
                  thinker who loves building beautiful digital experiences
                </Typography>
              </Box>

              {/* Chat Messages */}
              <Box
                ref={chatContainerRef}
                sx={{
                  height: 400,
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
                        Thinking...
                      </Typography>
                    </Paper>
                  </Box>
                )}
              </Box>

              {/* Input Area */}
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
                    placeholder="Ask me anything about Charlotte's experience, projects, or interests... ✨"
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

                <Typography
                  variant="caption"
                  sx={{
                    display: "block",
                    mt: 2,
                    textAlign: "center",
                    color: "text.secondary",
                    fontStyle: "italic",
                  }}
                >
                  Powered by Charlotte's passion for creating delightful user experiences 💕
                </Typography>
              </Box>
            </Paper>
          </Fade>
        </Container>
      </Box>
    </ThemeProvider>
  )
}

export default App
