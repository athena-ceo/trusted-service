'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Package,
  ChevronUp,
  ChevronDown,
  Trash2,
  Code,
  ChevronRight,
  ChevronDown as ChevronDownIcon,
} from 'lucide-react';
import axios from 'axios';
import RuleList from './RuleList';
import { Package as PackageType } from './types';
import PackageConditionEditor from './PackageConditionEditor';

interface PackageItemProps {
  runtime: string;
  app: string;
  package: PackageType;
  index: number;
  total: number;
  onMove: (packageName: string, direction: 'up' | 'down') => void;
  onDelete: (packageName: string) => void;
  isSelected?: boolean;
  isExpanded?: boolean;
  onToggleExpanded?: (packageName: string, expanded: boolean) => void;
}

export default function PackageItem({
  runtime,
  app,
  package: pkg,
  index,
  total,
  onMove,
  onDelete,
  isSelected = false,
  isExpanded: externalExpanded,
  onToggleExpanded,
}: PackageItemProps) {
  const [internalExpanded, setInternalExpanded] = useState(false);
  const isExpanded = externalExpanded !== undefined ? externalExpanded : internalExpanded;

  const handleToggleExpanded = () => {
    if (onToggleExpanded) {
      onToggleExpanded(pkg.name, !isExpanded);
    } else {
      setInternalExpanded(!isExpanded);
    }
  };;
  const [showConditionEditor, setShowConditionEditor] = useState(false);
  const queryClient = useQueryClient();

  const updateConditionMutation = useMutation({
    mutationFn: async (condition: string | null) => {
      const response = await axios.post(
        `/api/v1/ruleflow/runtime/${runtime}/apps/${app}/package/condition`,
        {
          package_name: pkg.name,
          condition: condition || null,
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ruleflow-structure', runtime, app] });
      setShowConditionEditor(false);
    },
  });

  return (
    <div className={`border rounded-lg overflow-hidden ${isSelected ? 'ring-2 ring-blue-500 border-blue-500' : ''}`}>
      <div className={`px-4 py-3 flex items-center justify-between ${isSelected ? 'bg-blue-50' : 'bg-gray-50'}`}>
        <div className="flex items-center gap-3 flex-1">
          <button
            onClick={handleToggleExpanded}
            className="text-gray-500 hover:text-gray-700"
          >
            {isExpanded ? (
              <ChevronDownIcon className="w-5 h-5" />
            ) : (
              <ChevronRight className="w-5 h-5" />
            )}
          </button>
          <Package className="w-5 h-5 text-blue-600" />
          <div className="flex-1">
            <div className="font-medium text-gray-900">{pkg.name}</div>
            {pkg.condition && (
              <div className="text-xs text-gray-600 mt-1 font-mono">
                Condition: {pkg.condition}
              </div>
            )}
            <div className="text-xs text-gray-500 mt-1">
              Order: {pkg.execution_order} • Rules: {pkg.rules.length}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowConditionEditor(true)}
            className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
            title="Edit condition"
          >
            <Code className="w-4 h-4" />
          </button>
          <button
            onClick={() => onMove(pkg.name, 'up')}
            disabled={index === 0}
            className="p-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Move up"
          >
            <ChevronUp className="w-4 h-4" />
          </button>
          <button
            onClick={() => onMove(pkg.name, 'down')}
            disabled={index === total - 1}
            className="p-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Move down"
          >
            <ChevronDown className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(pkg.name)}
            className="p-1.5 text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
            title="Delete package"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="p-4 bg-white">
          <RuleList
            runtime={runtime}
            app={app}
            packageName={pkg.name}
            rules={pkg.rules}
          />
        </div>
      )}

      {showConditionEditor && (
        <PackageConditionEditor
          runtime={runtime}
          app={app}
          packageName={pkg.name}
          currentCondition={pkg.condition || ''}
          onClose={() => setShowConditionEditor(false)}
          onSave={(condition) => updateConditionMutation.mutate(condition)}
        />
      )}
    </div>
  );
}



