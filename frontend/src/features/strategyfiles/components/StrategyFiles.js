import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '../../../components/ui/card';
import { FileText, ChevronDown, ChevronRight, Save } from 'lucide-react';
import CodeEditor from '@uiw/react-textarea-code-editor';
import { FONT_FAMILY } from '../constants';
import '../utils/editor-styles.css';

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

  const saveFileContent = async () => {
    if (!selectedFile) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/strategy-files/files/${selectedFile.path}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: fileContent }),
        }
      );

      if (!response.ok) throw new Error('Failed to save file');

      // 可以添加一个保存成功的提示
      alert('File saved successfully');
    } catch (err) {
      console.error('Save error:', err);
      alert('Failed to save file');
    }
  };

  const fetchStrategyFiles = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/strategy-files/files');
      if (!response.ok) throw new Error('Failed to fetch strategy files');
      const data = await response.json();
      
      // 按类别组织文件
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
          className="flex items-center p-2 bg-[#333333] rounded cursor-pointer transition-colors"
          onClick={() => toggleCategory(category)}
        >
          {expandedCategories[category] ?
            <ChevronDown className="h-4 w-4 mr-2 text-[#64ffda]" /> :
            <ChevronRight className="h-4 w-4 mr-2 text-[#64ffda]" />
          }
          <h3 className="font-medium text-[#64ffda]">{categoryTitles[category]}</h3>
          <span className="ml-2 text-[#888]">({files.length})</span>
        </div>

        {expandedCategories[category] && (
          <div className="pl-6 mt-2">
            {files.map((file, index) => (
              <div
                key={index}
                className={`flex items-center p-3 rounded cursor-pointer transition-colors
                  ${selectedFile?.name === file.name ? 'bg-[#333333]' : 'hover:bg-[#333333]'}`}
                onClick={() => fetchFileContent(file)}
              >
                <FileText className="h-5 w-5 mr-2 text-[#64ffda]" />
                <div>
                  <div className="font-medium text-white">{file.name}</div>
                  <div className="text-sm text-[#888]">
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
    return <div className="p-4 text-white">Loading strategy files...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-400">Error: {error}</div>;
  }

  return (
    <div className="flex h-full gap-4 bg-[#1a1a1a] p-4">
      {/* 文件列表侧边栏 */}
      <Card className="w-1/3 bg-[#2a2a2a] border-0">
        <CardHeader>
          <h2 className="text-xl font-medium text-white">Strategy Files</h2>
        </CardHeader>
        <CardContent>
          {Object.entries(files).map(([category, categoryFiles]) =>
            renderFileList(category, categoryFiles)
          )}
        </CardContent>
      </Card>

      {/* 修改右侧编辑器部分 */}
      <Card className="w-2/3 bg-[#2a2a2a] border-0">
        <CardHeader className="flex flex-row items-center justify-between border-b border-[#333333]">
          <h2 className="text-xl font-medium text-white">
            {selectedFile ? selectedFile.name : 'Select a file to view'}
          </h2>
          {selectedFile && (
            <button
              className="flex items-center px-4 py-2 bg-[#64ffda] text-black rounded hover:bg-[#4fd8b8] transition-colors"
              onClick={saveFileContent}
            >
              <Save className="h-4 w-4 mr-2" />
              Save
            </button>
          )}
        </CardHeader>
        <CardContent>
          {selectedFile ? (
            <div className="w-full h-[calc(100vh-300px)] rounded border border-[#333333]">
              <CodeEditor
                value={fileContent}
                language="python"
                placeholder="Enter your python code."
                onChange={(e) => setFileContent(e.target.value)}
                padding={15}
                style={{
                  fontSize: 14,
                  backgroundColor: "#1a1a1a",
                  fontFamily: FONT_FAMILY,
                  height: '100%',
                  overflowY: 'auto',
                  borderRadius: '4px',
                }}
                data-color-mode="dark"
              />
            </div>
          ) : (
            <div className="text-center text-[#888] py-4">
              No file selected
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
