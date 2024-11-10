const API_BASE_URL = 'http://127.0.0.1:8000/api/strategy';

export const useStrategyApi = () => {
  // 策略列表的方法
  const listStrategies = async (pageNum = 1, pageSize = 10) => {
    const response = await fetch(`${API_BASE_URL}/list_strategy?page_num=${pageNum}&page_size=${pageSize}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '获取策略列表失败');
    }

    return response.json();
  };


  // 策略创建的方法
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

  // 策略更新的方法
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

  const deleteStrategy = async (id) => {
    const response = await fetch(`${API_BASE_URL}/delete_strategy/${id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '删除策略失败');
    }

    return response.json();
  };

  const toggleStrategyStatus = async (id, active) => {
    const response = await fetch(`${API_BASE_URL}/toggle_strategy/${id}?active=${active}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '更新策略状态失败');
    }

    return response.json();
  };

  return {
    createStrategy,
    updateStrategy,
    listStrategies,
    deleteStrategy,
    toggleStrategyStatus,
  };
};