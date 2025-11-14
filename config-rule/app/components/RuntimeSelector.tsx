'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FolderOpen, ChevronDown, ChevronRight, Loader2 } from 'lucide-react';
import axios from 'axios';

interface RuntimeSelectorProps {
  selected: string | null;
  onSelect: (runtime: string) => void;
}

export default function RuntimeSelector({ selected, onSelect }: RuntimeSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newRuntimeName, setNewRuntimeName] = useState('');
  const queryClient = useQueryClient();

  const { data: runtimeDirs = [], isLoading } = useQuery({
    queryKey: ['runtime-directories'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/ruleflow/runtime-directories');
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: async (name: string) => {
      const response = await axios.post(`/api/v1/ruleflow/runtime/create?runtime_name=${name}`);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['runtime-directories'] });
      // Sélectionner automatiquement le nouveau runtime créé
      onSelect(variables);
      setNewRuntimeName('');
      setShowCreateDialog(false);
    },
  });

  const handleCreate = () => {
    if (!newRuntimeName.trim()) return;
    createMutation.mutate(newRuntimeName.trim());
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="w-full flex items-center justify-between px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <FolderOpen className="w-5 h-5 text-gray-500" />
              <span className={selected ? 'text-gray-900 font-medium' : 'text-gray-500'}>
                {selected || 'Select runtime...'}
              </span>
            </div>
            {isLoading ? (
              <Loader2 className="w-5 h-5 text-gray-500 animate-spin" />
            ) : isOpen ? (
              <ChevronDown className="w-5 h-5 text-gray-500" />
            ) : (
              <ChevronRight className="w-5 h-5 text-gray-500" />
            )}
          </button>

          {isOpen && !isLoading && (
            <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-60 overflow-auto">
              {runtimeDirs.length === 0 ? (
                <div className="px-4 py-2 text-gray-500 text-sm">
                  No runtime directories found
                </div>
              ) : (
                runtimeDirs.map((runtime: string) => (
                  <button
                    key={runtime}
                    onClick={() => {
                      onSelect(runtime);
                      setIsOpen(false);
                    }}
                    className={`w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors ${selected === runtime ? 'bg-blue-50 text-blue-600 font-medium' : ''
                      }`}
                  >
                    {runtime}
                  </button>
                ))
              )}
            </div>
          )}
        </div>
        <button
          onClick={() => setShowCreateDialog(true)}
          className="px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          title="Create new runtime"
        >
          New
        </button>
      </div>

      {showCreateDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Create New Runtime</h3>
            <input
              type="text"
              value={newRuntimeName}
              onChange={(e) => setNewRuntimeName(e.target.value)}
              placeholder="Runtime directory name"
              className="w-full px-3 py-2 border rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleCreate()}
              autoFocus
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setShowCreateDialog(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
                disabled={createMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={createMutation.isPending || !newRuntimeName.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {createMutation.isPending ? 'Creating...' : 'Create'}
              </button>
            </div>
            {createMutation.isError && (
              <div className="mt-2 text-sm text-red-600">
                Error creating runtime directory
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}



