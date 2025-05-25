import React, { useState, useEffect, useRef } from 'react';
import { Box, TextField, IconButton, Typography, Paper, Button } from '@material-ui/core';
import SendIcon from '@material-ui/icons/Send';
import { chatStream, adoptStrategy } from '../api/agent';
import { marked } from 'marked';
import hljs from 'highlight.js/lib/common';
import 'highlight.js/styles/github-dark.css';

marked.setOptions({
  highlight: (code, lang) => {
    try {
      return hljs.highlight(code, { language: lang || 'plaintext' }).value;
    } catch {
      return hljs.highlightAuto(code).value;
    }
  }
});

const MessageItem = ({ role, content, discarded }) => (
  <Box mb={2} display="flex" justifyContent={role === 'user' ? 'flex-end' : 'flex-start'}>
    <Paper style={{ padding: 12, maxWidth: '80%', background: role === 'user' ? '#2563eb' : discarded ? '#555' : '#1e1e1e', opacity: discarded ? 0.5 : 1 }}>
      <div
        className="markdown-preview"
        dangerouslySetInnerHTML={{ __html: marked(content) }}
      />
      {discarded && <Typography variant="caption" color="error">已废弃</Typography>}
    </Paper>
  </Box>
);

export default function ChatAgent() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const listRef = useRef();
  const [showActions, setShowActions] = useState(false);
  const [adoptType, setAdoptType] = useState('entry');

  const scrollBottom = () => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  };

  const getValidContext = () => {
    return messages.filter(m => !m.discarded && (m.role === 'user' || m.role === 'assistant')).map(m => ({ role: m.role, content: m.content }));
  };

  const handleSend = async (customInput) => {
    const sendContent = customInput !== undefined ? customInput : input;
    if (!sendContent.trim()) return;
    const newMsg = { role: 'user', content: sendContent };
    setMessages((prev) => [...prev, newMsg]);
    setInput('');

    const context = [...getValidContext(), { role: 'user', content: sendContent }];
    const es = await chatStream({ message: sendContent, messages: context });
    es.addEventListener('delta', (e) => {
      const delta = e.data;
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === 'assistant_stream') {
          updated[updated.length - 1] = { ...last, content: last.content + delta };
          return updated;
        }
        return [...updated, { role: 'assistant_stream', content: delta }];
      });
      scrollBottom();
    });
    es.addEventListener('end', () => {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last && last.role === 'assistant_stream') {
          last.role = 'assistant';
          return [...prev.slice(0, -1), last];
        }
        return prev;
      });
      setShowActions(true);
      es.close();
    });
  };

  const handleAdopt = async () => {
    const last = messages[messages.length - 1];
    if (!last || last.role !== 'assistant') return;
    await adoptStrategy({ cid: 'local', content: last.content, stype: adoptType });
    setShowActions(false);
    setMessages((prev) => [...prev, { role: 'system', content: `✅ 已采纳并保存为 ${adoptType} 策略文件` }]);
  };

  const handleRegenerate = () => {
    setShowActions(false);
    const lastUser = [...messages].reverse().find(m => m.role === 'user');
    if (lastUser) {
      handleSend(lastUser.content);
    }
  };

  const handleDiscard = () => {
    setShowActions(false);
    setMessages((prev) => {
      const updated = [...prev];
      for (let i = updated.length - 1; i >= 0; i--) {
        if (updated[i].role === 'assistant' && !updated[i].discarded) {
          updated[i] = { ...updated[i], discarded: true };
          break;
        }
      }
      return updated;
    });
  };

  useEffect(scrollBottom, [messages]);

  return (
    <Box height="calc(100vh - 120px)" display="flex" flexDirection="column">
      <Typography variant="h4" align="center" gutterBottom>策略处理 Agent</Typography>
      <Box ref={listRef} flex={1} overflow="auto" px={2} py={1}>
        {messages.map((m, idx) => (
          <MessageItem key={idx} role={m.role.startsWith('assistant') ? 'assistant' : m.role} content={m.content} discarded={m.discarded} />
        ))}
      </Box>
      <Box display="flex" px={2} py={1}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="输入策略描述或后续指令..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
        />
        <IconButton color="primary" onClick={() => handleSend()}><SendIcon /></IconButton>
      </Box>

      {showActions && (
        <Box display="flex" justifyContent="center" gap={2} py={1} alignItems="center">
          <Button variant="contained" color="primary" size="small" onClick={handleAdopt}>采纳</Button>
          <TextField
            select
            size="small"
            value={adoptType}
            onChange={e => setAdoptType(e.target.value)}
            style={{ width: 90, marginLeft: 8, marginRight: 8 }}
          >
            <option value="entry">entry</option>
            <option value="exit">exit</option>
            <option value="filter">filter</option>
          </TextField>
          <Button variant="outlined" size="small" onClick={handleRegenerate}>重新生成</Button>
          <Button variant="text" size="small" onClick={handleDiscard}>废弃</Button>
        </Box>
      )}
    </Box>
  );
} 