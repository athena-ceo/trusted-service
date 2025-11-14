'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import axios from 'axios';
import RuleItem from './RuleItem';
import { Rule } from './types';

interface RuleListProps {
  runtime: string;
  app: string;
  packageName: string;
  rules: Rule[];
}

export default function RuleList({ runtime, app, packageName, rules }: RuleListProps) {
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newRuleName, setNewRuleName] = useState('');
  const [newRuleCode, setNewRuleCode] = useState('');
  const queryClient = useQueryClient();

  // Génère automatiquement le template de code quand le nom change
  const handleRuleNameChange = (name: string) => {
    setNewRuleName(name);
    if (name.trim()) {
      const templateCode = `def rule_${name.trim()}(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
    output.details.append("rule_${name.trim()}")
    output.acknowledgement_to_requester = "#ACK"
    output.response_template_id = ""
    output.work_basket = "default"
    output.priority = "MEDIUM"
    output.handling = "DEFLECTION"
    # Add your custom rule logic here`;
      setNewRuleCode(templateCode);
    } else {
      setNewRuleCode('');
    }
  };

  const addMutation = useMutation({
    mutationFn: async ({ ruleName, ruleCode }: { ruleName: string; ruleCode: string }) => {
      const response = await axios.post(
        `/api/v1/ruleflow/runtime/${runtime}/apps/${app}/rule/add`,
        {
          package_name: packageName,
          rule_name: `rule_${ruleName}`,
          rule_code: ruleCode,
          condition: null,
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ruleflow-structure', runtime, app] });
      setNewRuleName('');
      setNewRuleCode('');
      setShowAddDialog(false);
    },
  });

  const handleCloseDialog = () => {
    setNewRuleName('');
    setNewRuleCode('');
    setShowAddDialog(false);
  };

  const deleteMutation = useMutation({
    mutationFn: async (ruleName: string) => {
      const response = await axios.delete(
        `/api/v1/ruleflow/runtime/${runtime}/apps/${app}/rule/${packageName}/${ruleName}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ruleflow-structure', runtime, app] });
    },
  });

  const moveMutation = useMutation({
    mutationFn: async ({ ruleName, direction }: { ruleName: string; direction: string }) => {
      const response = await axios.post(
        `/api/v1/ruleflow/runtime/${runtime}/apps/${app}/rule/move`,
        { direction },
        {
          params: {
            package_name: packageName,
            rule_name: ruleName,
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ruleflow-structure', runtime, app] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ ruleName, code, condition }: { ruleName: string; code: string; condition?: string | null }) => {
      const response = await axios.post(
        `/api/v1/ruleflow/runtime/${runtime}/apps/${app}/rule/update`,
        {
          package_name: packageName,
          rule_name: ruleName,
          code,
          condition: condition || null,
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ruleflow-structure', runtime, app] });
    },
  });

  const handleAdd = () => {
    if (!newRuleName.trim() || !newRuleCode.trim()) return;

    addMutation.mutate({
      ruleName: newRuleName.trim(),
      ruleCode: newRuleCode.trim(),
    });
  };

  const handleMove = (ruleName: string, direction: 'up' | 'down') => {
    moveMutation.mutate({ ruleName, direction });
  };

  const handleDelete = (ruleName: string) => {
    if (confirm(`Are you sure you want to delete rule ${ruleName}?`)) {
      deleteMutation.mutate(ruleName);
    }
  };

  const handleUpdate = (ruleName: string, code: string, condition?: string | null) => {
    updateMutation.mutate({ ruleName, code, condition });
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">Rules</h3>
        <button
          onClick={() => setShowAddDialog(true)}
          className="flex items-center gap-1 px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
        >
          <Plus className="w-3 h-3" />
          Add Rule
        </button>
      </div>

      <div className="space-y-2">
        {rules.map((rule, index) => (
          <RuleItem
            key={rule.name}
            runtime={runtime}
            app={app}
            packageName={packageName}
            rule={rule}
            index={index}
            total={rules.length}
            onMove={handleMove}
            onDelete={handleDelete}
            onUpdate={handleUpdate}
          />
        ))}
        {rules.length === 0 && (
          <div className="text-sm text-gray-500 text-center py-4">
            No rules yet. Add your first rule.
          </div>
        )}
      </div>

      {showAddDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-auto">
            <h3 className="text-lg font-semibold mb-4">Add New Rule</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rule Name (without 'rule_' prefix)
                </label>
                <input
                  type="text"
                  value={newRuleName}
                  onChange={(e) => handleRuleNameChange(e.target.value)}
                  placeholder="rule_name"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rule Code
                </label>
                <textarea
                  value={newRuleCode}
                  onChange={(e) => setNewRuleCode(e.target.value)}
                  placeholder="Rule code will be auto-generated when you enter a rule name above"
                  className="w-full px-3 py-2 border rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  rows={12}
                />
              </div>
            </div>
            <div className="flex gap-2 justify-end mt-4">
              <button
                onClick={handleCloseDialog}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
                disabled={addMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={handleAdd}
                disabled={addMutation.isPending || !newRuleName.trim() || !newRuleCode.trim()}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {addMutation.isPending ? 'Adding...' : 'Add Rule'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}



