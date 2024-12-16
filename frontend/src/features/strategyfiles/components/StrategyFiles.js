import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '../../../components/ui/card';
import { FileText, ChevronDown, ChevronRight, Save } from 'lucide-react';

export default function StrategyFiles() {
  const [files, setFiles] = useState({
    entry_strategy: [],
    exit_strategy: [],
    filter_strategy: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [expandedCategories, setExpandedCategories] = useState({
    entry_strategy: true,
    exit_strategy: true,
    filter_strategy: true
  });

  useEffect(() => {
    fetchStrategyFiles();
  }, []);

  const fetchStrategyFiles = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/strategy-files/files');
      if (!response.ok) throw new Error('Failed to fetch strategy files');
      const data = await response.json();

      // 将文件按类别组织
      const categorizedFiles = {
        entry_strategy: [],
        exit_strategy: [],
        filter_strategy: []
      };

      data.forEach(file => {
        const category = file.path.split('/')[0];
        if (categorizedFiles[category]) {
          categorizedFiles[category].push(file);
        }
      });

      setFiles(categorizedFiles);
      setLoading(false);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const fetchFileContent = async (file) => {
    try {
      const response = await fetch(`http://localhost:8000/api/strategy-files/files/${file.path}`);
      if (!response.ok) throw new Error('Failed to fetch file content');
      const data = await response.json();
      setFileContent(data.content);
      setSelectedFile(file);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err.message);
    }
  };

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const renderFileList = (category, files) => {
    const categoryTitles = {
      entry_strategy: "入场策略",
      exit_strategy: "出场策略",
      filter_strategy: "过滤策略"
    };

    return (
      <div key={category} className="mb-4">
        <div
          className="flex items-center p-2 bg-gray-100 rounded cursor-pointer"
          onClick={() => toggleCategory(category)}
        >
          {expandedCategories[category] ?
            <ChevronDown className="h-4 w-4 mr-2" /> :
            <ChevronRight className="h-4 w-4 mr-2" />
          }
          <h3 className="font-semibold">{categoryTitles[category]}</h3>
          <span className="ml-2 text-gray-500">({files.length})</span>
        </div>

        {expandedCategories[category] && (
          <div className="pl-6">
            {files.map((file, index) => (
              <div
                key={index}
                className={`flex items-center p-3 rounded-lg hover:bg-gray-100 cursor-pointer ${
                  selectedFile?.name === file.name ? 'bg-gray-100' : ''
                }`}
                onClick={() => fetchFileContent(file)}
              >
                <FileText className="h-5 w-5 mr-2 text-blue-500" />
                <div>
                  <div className="font-medium">{file.name}</div>
                  <div className="text-sm text-gray-500">
                    Last modified: {new Date(file.modified).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return <div className="p-4">Loading strategy files...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="flex h-full gap-4">
      {/* 文件列表侧边栏 */}
      <Card className="w-1/3">
        <CardHeader>
          <h2 className="text-2xl font-bold">Strategy Files</h2>
        </CardHeader>
        <CardContent>
          {Object.entries(files).map(([category, categoryFiles]) =>
            renderFileList(category, categoryFiles)
          )}
        </CardContent>
      </Card>

      {/* 文件内容预览/编辑区域 */}
      <Card className="w-2/3">
        <CardHeader className="flex flex-row items-center justify-between">
          <h2 className="text-2xl font-bold">
            {selectedFile ? selectedFile.name : 'Select a file to view'}
          </h2>
          {selectedFile && (
            <button className="flex items-center px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
              <Save className="h-4 w-4 mr-2" />
              Save
            </button>
          )}
        </CardHeader>
        <CardContent>
          {selectedFile ? (
            <textarea
              className="w-full h-[calc(100vh-300px)] p-4 font-mono bg-gray-50 rounded border"
              value={fileContent}
              onChange={(e) => setFileContent(e.target.value)}
            />
          ) : (
            <div className="text-center text-gray-500 py-4">
              No file selected
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}