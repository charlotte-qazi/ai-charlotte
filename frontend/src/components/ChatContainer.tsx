/*
 * AI Charlotte - Reusable Chat Container Component
 * Copyright (c) 2025 Charlotte Qazi
 * 
 * This project is created and maintained by Charlotte Qazi.
 * For more information, visit: https://github.com/charlotteqazi
 * 
 * Licensed under the MIT License.
 */

import React, { useEffect, useRef } from 'react'
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

export interface ChatMessage {
  id: number
  role: 'assistant' | 'user'
  content: string
  timestamp: Date
}

interface ChatContainerProps {
  messages: ChatMessage[]
  inputValue: string
  onInputChange: (value: string) => void
  onSendMessage: () => void
  loading: boolean
  placeholder?: string
  loadingText?: string
}

const ChatContainer: React.FC<ChatContainerProps> = ({
  messages,
  inputValue,
  onInputChange,
  onSendMessage,
  loading,
  placeholder = "Type your message... ✨",
  loadingText = "Thinking..."
}) => {
  const chatContainerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    const scrollToBottom = () => {
      if (chatContainerRef.current) {
        try {
          chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
        } catch (error) {
          // Silently handle any scrolling errors
          console.debug('Scroll error:', error)
        }
      }
    }

    // Use a small delay to ensure DOM is fully rendered
    const timeoutId = setTimeout(scrollToBottom, 100)
    return () => clearTimeout(timeoutId)
  }, [messages])

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      onSendMessage()
    }
  }

  return (
    <Paper
      elevation={0}
      sx={{
        borderRadius: 4,
        overflow: "hidden",
        background: "rgba(255, 255, 255, 0.95)",
        backdropFilter: "blur(10px)",
        height: "100%",
        maxHeight: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Header */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #d7288b 0%, #ffbed5 100%)",
          p: 3,
          textAlign: "center",
          color: "white",
          flexShrink: 0,
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
          flex: 1,
          minHeight: 0,
          overflowY: "auto",
          overflowX: "hidden",
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
                {loadingText}
              </Typography>
            </Paper>
          </Box>
        )}
      </Box>

      {/* Input Area */}
      <Box
        sx={{
          flexShrink: 0,
          p: 3,
          borderTop: "1px solid #e9ecef",
          background: "rgba(248, 249, 250, 0.5)",
          minHeight: "100px", // Minimum height to ensure adequate space
        }}
      >
        <Box sx={{ display: "flex", gap: 2, alignItems: "flex-end" }}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
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
            onClick={onSendMessage}
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
  )
}

export default ChatContainer 