import { useState } from 'react'
import {
  Box,
  Container,
  CssBaseline,
  Paper,
  TextField,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    const trimmed = input.trim()
    if (!trimmed) return
    const userMessage: Message = { role: 'user', content: trimmed }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)
    try {
      const resp = await axios.post('/api/chat', { message: trimmed })
      const answer: string = resp.data.answer
      setMessages((prev) => [...prev, { role: 'assistant', content: answer }])
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <>
      <CssBaseline />
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Typography variant="h5" gutterBottom>
          AI Charlotte - Chat
        </Typography>
        <Paper variant="outlined" sx={{ p: 2, height: '60vh', overflow: 'auto' }}>
          {messages.length === 0 ? (
            <Typography color="text.secondary">Ask me about my CV or blog.</Typography>
          ) : (
            <List>
              {messages.map((m, idx) => (
                <ListItem key={idx} alignItems="flex-start">
                  <ListItemText
                    primary={m.role === 'user' ? 'You' : 'Assistant'}
                    secondary={m.content}
                  />
                </ListItem>
              ))}
              {loading && (
                <Box display="flex" justifyContent="center" py={2}>
                  <CircularProgress size={20} />
                </Box>
              )}
            </List>
          )}
        </Paper>
        <Box display="flex" gap={1} mt={2}>
          <TextField
            fullWidth
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
          />
          <IconButton color="primary" onClick={sendMessage} disabled={loading}>
            <SendIcon />
          </IconButton>
        </Box>
      </Container>
    </>
  )
}
