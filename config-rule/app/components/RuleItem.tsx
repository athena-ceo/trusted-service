'use client';

import { useState } from 'react';
import {
  ChevronUp,
  ChevronDown,
  Trash2,
  Edit2,
  ChevronRight,
  ChevronDown as ChevronDownIcon,
  Code as CodeIcon,
} from 'lucide-react';
import { Rule } from './types';
import RuleEditor from './RuleEditor';

interface RuleItemProps {
  runtime: string;
  app: string;
  packageName: string;
  rule: Rule;
  index: number;
  total: number;
  onMove: (ruleName: string, direction: 'up' | 'down') => void;
  onDelete: (ruleName: string) => void;
  onUpdate: (ruleName: string, code: string, condition?: string | null) => void;
}

export default function RuleItem({
  runtime,
  app,
  packageName,
  rule,
  index,
  total,
  onMove,
  onDelete,
  onUpdate,
}: RuleItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showEditor, setShowEditor] = useState(false);

  const handleSave = (code: string, condition?: string | null) => {
    onUpdate(rule.name, code, condition);
    setShowEditor(false);
  };

  return (
    <>
      <div className="border rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-3 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2 flex-1">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-gray-500 hover:text-gray-700"
            >
              {isExpanded ? (
                <ChevronDownIcon className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
            <CodeIcon className="w-4 h-4 text-purple-600" />
            <div className="flex-1">
              <div className="font-medium text-sm text-gray-900">{rule.name}</div>
              {rule.condition && (
                <div className="text-xs text-gray-600 mt-0.5 font-mono">
                  Condition: {rule.condition}
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setShowEditor(true)}
              className="p-1 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
              title="Edit rule"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => onMove(rule.name, 'up')}
              disabled={index === 0}
              className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Move up"
            >
              <ChevronUp className="w-4 h-4" />
            </button>
            <button
              onClick={() => onMove(rule.name, 'down')}
              disabled={index === total - 1}
              className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Move down"
            >
              <ChevronDown className="w-4 h-4" />
            </button>
            <button
              onClick={() => onDelete(rule.name)}
              className="p-1 text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
              title="Delete rule"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {isExpanded && (
          <div className="p-3 bg-white border-t">
            <pre className="text-xs font-mono bg-gray-50 p-3 rounded overflow-x-auto">
              <code>{rule.code}</code>
            </pre>
          </div>
        )}
      </div>

      {showEditor && (
        <RuleEditor
          runtime={runtime}
          app={app}
          packageName={packageName}
          rule={rule}
          onClose={() => setShowEditor(false)}
          onSave={handleSave}
        />
      )}
    </>
  );
}



