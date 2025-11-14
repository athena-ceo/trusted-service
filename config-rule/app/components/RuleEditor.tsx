'use client';

import { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Rule } from './types';

interface RuleEditorProps {
  runtime: string;
  app: string;
  packageName: string;
  rule: Rule;
  onClose: () => void;
  onSave: (code: string, condition?: string | null) => void;
}

export default function RuleEditor({
  rule,
  onClose,
  onSave,
}: RuleEditorProps) {
  const [code, setCode] = useState(rule.code);
  const [condition, setCondition] = useState(rule.condition || '');

  useEffect(() => {
    setCode(rule.code);
    setCondition(rule.condition || '');
  }, [rule]);

  const handleSave = () => {
    onSave(code, condition.trim() || null);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold">Edit Rule: {rule.name}</h3>
          <button
            onClick={onClose}
            className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-auto p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Condition (optional)
            </label>
            <input
              type="text"
              value={condition}
              onChange={(e) => setCondition(e.target.value)}
              placeholder='e.g., input.intention_id == "expiration_d_une_api"'
              className="w-full px-3 py-2 border rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Python expression that determines when this rule executes
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Rule Code
            </label>
            <div className="border rounded-lg overflow-hidden">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full px-3 py-2 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={20}
                style={{ fontFamily: 'monospace' }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Python function definition for this rule
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preview
            </label>
            <div className="border rounded-lg overflow-hidden bg-gray-900">
              <SyntaxHighlighter
                language="python"
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: '0.5rem' }}
              >
                {code}
              </SyntaxHighlighter>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 p-4 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Save className="w-4 h-4" />
            Save
          </button>
        </div>
      </div>
    </div>
  );
}



