// Agent related API calls
const BASE_URL = 'http://localhost:8000';

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || '请求失败');
  }
  return response.json();
};

export const listPrompts = async () => {
  const response = await fetch(`${BASE_URL}/api/agent/prompts`);
  return handleResponse(response);
};

export const createPrompt = async (data) => {
  const response = await fetch(`${BASE_URL}/api/agent/prompts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return handleResponse(response);
};

export const updatePrompt = async (id, data) => {
  const response = await fetch(`${BASE_URL}/api/agent/prompts/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return handleResponse(response);
};

export const deletePrompt = async (id) => {
  const response = await fetch(`${BASE_URL}/api/agent/prompts/${id}`, {
    method: 'DELETE'
  });
  return handleResponse(response);
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${BASE_URL}/api/agent/files`, {
    method: 'POST',
    body: formData
  });
  return handleResponse(response);
};

export const startJob = async (fileId, promptId) => {
  const response = await fetch(`${BASE_URL}/api/agent/jobs?file_id=${fileId}&prompt_id=${promptId}`, {
    method: 'POST'
  });
  return handleResponse(response);
};

export const jobStatus = async (jobId) => {
  const response = await fetch(`${BASE_URL}/api/agent/jobs/${jobId}`);
  return handleResponse(response);
};

export const downloadCode = async (jobId) => {
  const response = await fetch(`${BASE_URL}/api/agent/jobs/${jobId}/code`);
  if (!response.ok) {
    throw new Error('下载失败');
  }
  return response.blob();
};

export const listFiles = async () => {
  const response = await fetch(`${BASE_URL}/api/agent/files`);
  return handleResponse(response);
};

export const downloadRaw = async (fileId) => {
  const response = await fetch(`${BASE_URL}/api/agent/files/${fileId}/raw`);
  if (!response.ok) throw new Error('下载失败');
  return response.blob();
};

// -------- Chat (new) ---------

// 普通一次性返回
export const chatOnce = async (body) => {
  const response = await fetch(`${BASE_URL}/api/agent/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return handleResponse(response);
};

// 流式：返回 EventSource 实例，由调用方监听 message
export const chatStream = async (body) => {
  // 1. 创建通道，获取 cid
  const res = await fetch(`${BASE_URL}/api/agent/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const { cid } = await res.json();
  // 2. 打开 SSE
  return new EventSource(`${BASE_URL}/api/agent/chat/stream/${cid}`);
};

export const adoptStrategy = async (payload) => {
  const response = await fetch(`${BASE_URL}/api/agent/adopt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return handleResponse(response);
};

export const startEvaluate = async (payload) => {
  const response = await fetch(`${BASE_URL}/api/agent/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return handleResponse(response);
};

export const getEvaluate = async (jobId) => {
  const response = await fetch(`${BASE_URL}/api/agent/evaluate/${jobId}`);
  return handleResponse(response);
}; 