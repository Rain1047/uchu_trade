const API_BASE_URL = 'http://127.0.0.1:8000/api/strategy';

export const useStrategyApi = () => {
  const createStrategy = async (data) => {
    const response = await fetch(`${API_BASE_URL}/create_strategy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '创建策略失败');
    }

    return response.json();
  };

  const updateStrategy = async (id, data) => {
    const response = await fetch(`${API_BASE_URL}/update_strategy/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '更新策略失败');
    }

    return response.json();
  };

  return {
    createStrategy,
    updateStrategy,
  };
};