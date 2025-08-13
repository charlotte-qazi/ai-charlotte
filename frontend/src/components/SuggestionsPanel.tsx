/*
 * AI Charlotte - Conversation Suggestions Panel
 * Copyright (c) 2025 Charlotte Qazi
 * 
 * This project is created and maintained by Charlotte Qazi.
 * For more information, visit: https://github.com/charlotteqazi
 * 
 * Licensed under the MIT License.
 */

import React from 'react'
import { Box, Button, Typography, Paper } from '@mui/material'
import { 
  Psychology as PsychologyIcon,
  Work as WorkIcon, 
  Code as CodeIcon,
  Groups as GroupsIcon,
  Lightbulb as LightbulbIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material'

interface SuggestionsPanelProps {
  onSuggestionClick: (message: string) => void
  disabled?: boolean
}

const suggestions = [
  {
    icon: <WorkIcon />,
    text: "What is Charlotte's experience at BCG?",
    category: "Experience"
  },
  {
    icon: <CodeIcon />,
    text: "What are Charlotte's technical skills?",
    category: "Skills"
  },
  {
    icon: <PsychologyIcon />,
    text: "Tell me about Charlotte's AI projects",
    category: "AI Projects"
  },
  {
    icon: <GroupsIcon />,
    text: "What leadership experience does Charlotte have?",
    category: "Leadership"
  },
  {
    icon: <LightbulbIcon />,
    text: "What are your thoughts on building Gen AI for humans?",
    category: "Insights"
  },
  {
    icon: <TrendingUpIcon />,
    text: "How did Charlotte transition into tech?",
    category: "Career"
  }
]

const SuggestionsPanel: React.FC<SuggestionsPanelProps> = ({ 
  onSuggestionClick, 
  disabled = false 
}) => {
  return (
    <Paper
      elevation={0}
      sx={{
        borderRadius: 4,
        overflow: "hidden",
        background: "rgba(255, 255, 255, 0.95)",
        backdropFilter: "blur(10px)",
        height: "100%",
        p: 3,
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography 
          variant="h6" 
          gutterBottom 
          sx={{ 
            fontWeight: 600, 
            color: "primary.main",
            display: "flex",
            alignItems: "center",
            gap: 1
          }}
        >
          💡 Quick Start
        </Typography>
        <Typography 
          variant="body2" 
          sx={{ 
            color: "text.secondary",
            lineHeight: 1.5
          }}
        >
          Click any question below to start a conversation
        </Typography>
      </Box>

      {/* Suggestion Buttons */}
      <Box sx={{ 
        display: "flex", 
        flexDirection: "column", 
        gap: 1.5,
        flex: 1
      }}>
        {suggestions.map((suggestion, index) => (
          <Button
            key={index}
            variant="outlined"
            disabled={disabled}
            onClick={() => onSuggestionClick(suggestion.text)}
            sx={{
              textAlign: "left",
              justifyContent: "flex-start",
              p: 2,
              borderRadius: 3,
              borderColor: "rgba(215, 40, 139, 0.2)",
              bgcolor: "transparent",
              color: "text.primary",
              textTransform: "none",
              fontSize: "0.875rem",
              lineHeight: 1.4,
              minHeight: "auto",
              "&:hover": {
                bgcolor: "rgba(215, 40, 139, 0.05)",
                borderColor: "primary.main",
                transform: "translateY(-1px)",
                boxShadow: "0 4px 12px rgba(215, 40, 139, 0.15)",
              },
              "&:active": {
                transform: "translateY(0px)",
              },
              "&.Mui-disabled": {
                opacity: 0.5,
                cursor: "not-allowed",
              },
              transition: "all 0.2s ease-in-out",
              display: "flex",
              alignItems: "center",
              gap: 1.5,
            }}
          >
            <Box sx={{ 
              color: "primary.main", 
              display: "flex",
              alignItems: "center",
              flexShrink: 0
            }}>
              {suggestion.icon}
            </Box>
            <Box sx={{ textAlign: "left", flex: 1 }}>
              <Typography variant="caption" sx={{ 
                color: "primary.main", 
                fontWeight: 500,
                display: "block",
                fontSize: "0.7rem",
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                mb: 0.5
              }}>
                {suggestion.category}
              </Typography>
              <Typography variant="body2" sx={{ 
                color: "text.primary",
                fontWeight: 400,
                lineHeight: 1.3
              }}>
                {suggestion.text}
              </Typography>
            </Box>
          </Button>
        ))}
      </Box>

      {/* Footer */}
      <Box sx={{ mt: 2, textAlign: "center" }}>
        <Typography 
          variant="caption" 
          sx={{ 
            color: "text.secondary",
            fontStyle: "italic",
            fontSize: "0.75rem"
          }}
        >
          Or type your own question in the chat ✨
        </Typography>
      </Box>
    </Paper>
  )
}

export default SuggestionsPanel 