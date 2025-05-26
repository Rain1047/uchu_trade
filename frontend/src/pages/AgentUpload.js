import React, { useEffect, useState, useRef } from 'react';
import {
  Box,
  Button,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
  LinearProgress,
  TextField,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle
} from '@material-ui/core';
import { uploadFile, listPrompts, createPrompt, startJob, jobStatus, downloadCode, listFiles, downloadRaw } from '../api/agent';
import { marked } from 'marked';
import hljs from 'highlight.js/lib/common';
import 'highlight.js/styles/github-dark.css';

// 配置 marked 的代码高亮
marked.setOptions({
  highlight: (code, lang) => {
    try {
      return hljs.highlight(code, { language: lang || 'plaintext' }).value;
    } catch (_) {
      return hljs.highlightAuto(code).value;
    }
  }
});

const AgentUpload = () => {
  const [file, setFile] = useState(null);
  const [prompts, setPrompts] = useState([]);
  const [promptId, setPromptId] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [jobId, setJobId] = useState(null);
  const [newPromptOpen, setNewPromptOpen] = useState(false);
  const [newPromptName, setNewPromptName] = useState('');
  const [newPromptContent, setNewPromptContent] = useState('');
  const [files, setFiles] = useState([]);
  const fileInputRef = useRef();
  const previewRef = useRef();

  useEffect(() => {
    fetchPrompts();
  }, []);

  useEffect(() => {
    let timer;
    if (jobId) {
      timer = setInterval(() => {
        jobStatus(jobId).then((data) => {
          setProgress(data.progress);
          if (data.status === 'success' || data.status === 'error') {
            clearInterval(timer);
            setLoading(false);
            if (data.status === 'success') {
              downloadCode(jobId).then((blob) => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${jobId}.py`;
                a.click();
                window.URL.revokeObjectURL(url);
              });
            } else {
              alert('生成失败：' + data.message);
            }
          }
        });
      }, 2000);
    }
    return () => clearInterval(timer);
  }, [jobId]);

  useEffect(() => {
    // 获取文件列表
    listFiles().then(setFiles).catch(console.error);
  }, []);

  useEffect(() => {
    if (previewRef.current) {
      previewRef.current.querySelectorAll('pre code').forEach(block => {
        hljs.highlightElement(block);
      });
    }
  }, [newPromptContent]);

  const fetchPrompts = () => {
    console.log('Fetching prompts...');
    listPrompts()
      .then((data) => {
        console.log('Prompts data:', data);
        setPrompts(data);
      })
      .catch(error => {
        console.error('Error fetching prompts:', error);
        alert('获取Prompts失败: ' + (error.response?.data?.detail || error.message));
      });
  };

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f && f.size > 20 * 1024 * 1024) {
      alert('文件大小不能超过20MB');
      return;
    }
    setFile(f);
  };

  const handleUpload = async () => {
    if (!file || !promptId) return alert('请选择文件和Prompt');
    try {
      setLoading(true);
      const fileRes = await uploadFile(file);
      const { id: fileId } = fileRes;
      const jobRes = await startJob(fileId, promptId);
      setJobId(jobRes.id);
    } catch (e) {
      console.error(e);
      alert('上传或任务创建失败');
      setLoading(false);
    }
  };

  const handleCreatePrompt = () => {
    createPrompt({ name: newPromptName, content: newPromptContent }).then(() => {
      setNewPromptOpen(false);
      setNewPromptName('');
      setNewPromptContent('');
      fetchPrompts();
    });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        策略处理 Agent
      </Typography>

      <Box mb={2} display="flex" alignItems="center" gap={2}>
        <input
          type="file"
          accept=".pdf,.epub"
          style={{ display: 'none' }}
          ref={fileInputRef}
          onChange={handleFileChange}
        />
        <Button variant="outlined" onClick={() => fileInputRef.current.click()}>选择文件</Button>
        {file && <Typography variant="body2">已选：{file.name}</Typography>}
      </Box>

      <FormControl variant="outlined" size="small" style={{ minWidth: 220 }}>
        <InputLabel>选择SystemPrompt</InputLabel>
        <Select value={promptId} onChange={(e) => setPromptId(e.target.value)} label="选择SystemPrompt">
          {prompts.map((p) => (
            <MenuItem value={p.id} key={p.id}>
              {p.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Button color="primary" variant="outlined" onClick={() => setNewPromptOpen(true)} style={{ marginLeft: 16 }}>
        新建Prompt
      </Button>

      <Box mt={3} display="flex" gap={2}>
        <Button variant="contained" color="primary" disabled={loading} onClick={handleUpload}>
          开始生成策略
        </Button>
      </Box>

      {loading && (
        <Box mt={3} width="100%">
          <LinearProgress variant="determinate" value={progress} />
          <Typography variant="body2" align="center">{progress}%</Typography>
        </Box>
      )}

      {/* 新建 Prompt 对话框 */}
      <Dialog open={newPromptOpen} onClose={() => setNewPromptOpen(false)} maxWidth="lg" fullWidth PaperProps={{ style: { borderRadius: 12 } }}>
        <DialogTitle>新建 SystemPrompt</DialogTitle>
        <DialogContent style={{ height: '70vh' }}>
          <Box style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', columnGap: 24, height: '100%', width: '100%' }}>
            {/* 编辑器在左 */}
            <Box style={{ display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden' }}>
              <TextField label="名称" fullWidth margin="normal" value={newPromptName} onChange={(e) => setNewPromptName(e.target.value)} />
              <TextField
                label="Markdown 内容"
                fullWidth
                multiline
                rows={20}
                margin="normal"
                value={newPromptContent}
                onChange={(e) => setNewPromptContent(e.target.value)}
                variant="outlined"
                style={{ flex: 1 }}
              />
            </Box>
            {/* 预览在右 */}
            <Box style={{ backgroundColor: '#1e1e1e', border: '1px solid #30363d', borderRadius: 8, padding: 16, overflow: 'auto', minWidth: 0 }}>
              <Typography variant="subtitle1" gutterBottom>预览</Typography>
              <div ref={previewRef} className="markdown-preview" dangerouslySetInnerHTML={{ __html: marked(newPromptContent || '') }} />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewPromptOpen(false)}>取消</Button>
          <Button onClick={handleCreatePrompt} color="primary" variant="contained">保存</Button>
        </DialogActions>
      </Dialog>

      <Box mt={4}>
        <Typography variant="h6" gutterBottom>已上传文件</Typography>
        <ul>
          {files.map(f => (
            <li key={f.id}>
              {f.filename} ({(f.size/1024/1024).toFixed(2)} MB)
              <Button size="small" color="primary" onClick={() => {
                downloadRaw(f.id).then(blob => {
                  const url = window.URL.createObjectURL(blob);
                  window.open(url, '_blank');
                  // 不 revoke 让浏览器继续查看
                });
              }} style={{marginLeft:8}}>预览</Button>
            </li>
          ))}
        </ul>
      </Box>
    </Box>
  );
};

export default AgentUpload; 