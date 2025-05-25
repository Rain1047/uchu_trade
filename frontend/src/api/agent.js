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