'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Package, ChevronDown, ChevronRight, Loader2 } from 'lucide-react';
import axios from 'axios';

interface AppSelectorProps {
  runtime: string;
  selected: string | null;
  onSelect: (app: string) => void;
}

export default function AppSelector({ runtime, selected, onSelect }: AppSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [userClosedDialog, setUserClosedDialog] = useState(false);
  const [newAppName, setNewAppName] = useState('');
  const [newClassName, setNewClassName] = useState('');
  const queryClient = useQueryClient();

  const { data: apps = [], isLoading } = useQuery({
    queryKey: ['apps', runtime],
    queryFn: async () => {
      const response = await axios.get(`/api/v1/ruleflow/runtime/${runtime}/apps`);
      return response.data;
    },
    enabled: !!runtime,
  });

  // Ouvrir automatiquement le dialog de création si aucune app n'existe
  useEffect(() => {
    if (!isLoading && apps.length === 0 && runtime && !showCreateDialog && !userClosedDialog) {
      setShowCreateDialog(true);
    }
  }, [apps, isLoading, runtime, showCreateDialog, userClosedDialog]);

  // Réinitialiser le flag quand on change de runtime
  useEffect(() => {
    setUserClosedDialog(false);
  }, [runtime]);

  const createMutation = useMutation({
    mutationFn: async ({ appName, className }: { appName: string; className: string }) => {
      const response = await axios.post(`/api/v1/ruleflow/runtime/${runtime}/apps/create`, {
        runtime_dir: runtime,
        app_name: appName,
        class_name: className || 'DecisionEngine',
      });
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['apps', runtime] });
      // Sélectionner automatiquement la nouvelle app créée
      onSelect(variables.appName);
      setNewAppName('');
      setNewClassName('');
      setShowCreateDialog(false);
      setUserClosedDialog(false); // Réinitialiser le flag
    },
  });

  const handleCloseDialog = () => {
    setUserClosedDialog(true);
    setShowCreateDialog(false);
    setNewAppName('');
    setNewClassName('');
  };
  const handleCreate = () => {
    if (!newAppName.trim()) return;
    createMutation.mutate({
      appName: newAppName.trim(),
      className: newClassName.trim() || 'DecisionEngine',
    });
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
              <Package className="w-5 h-5 text-gray-500" />
              <span className={selected ? 'text-gray-900 font-medium' : 'text-gray-500'}>
                {selected || (apps.length === 0 && !isLoading ? 'No applications yet - create one above' : 'Select an application...')}
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
              {apps.length === 0 ? (
                <div className="px-4 py-2 text-gray-500 text-sm">
                  No applications yet. Create your first app using the "New" button.
                </div>
              ) : (
                apps.map((app: string) => (
                  <button
                    key={app}
                    onClick={() => {
                      onSelect(app);
                      setIsOpen(false);
                    }}
                    className={`w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors ${selected === app ? 'bg-green-50 text-green-600 font-medium' : ''
                      }`}
                  >
                    {app}
                  </button>
                ))
              )}
            </div>
          )}
        </div>
        <button
          onClick={() => setShowCreateDialog(true)}
          className="px-3 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          title="Create new application"
        >
          New
        </button>
      </div>

      {/* Message d'encouragement si l'utilisateur a fermé le dialog et qu'il n'y a pas d'apps */}
      {!isLoading && apps.length === 0 && userClosedDialog && (
        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-700">
            💡 <strong>Ready to get started?</strong> Create your first application to begin building your decision engine rules.
          </p>
        </div>
      )}

      {showCreateDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Create New App</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  App Name
                </label>
                <input
                  type="text"
                  value={newAppName}
                  onChange={(e) => setNewAppName(e.target.value)}
                  placeholder="app_name"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  onKeyPress={(e) => e.key === 'Enter' && handleCreate()}
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Class Name (optional)
                </label>
                <input
                  type="text"
                  value={newClassName}
                  onChange={(e) => setNewClassName(e.target.value)}
                  placeholder="DecisionEngine"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  onKeyPress={(e) => e.key === 'Enter' && handleCreate()}
                />
              </div>
            </div>
            <div className="flex gap-2 justify-end mt-4">
              <button
                onClick={handleCloseDialog}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
                disabled={createMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={createMutation.isPending || !newAppName.trim()}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {createMutation.isPending ? 'Creating...' : 'Create'}
              </button>
            </div>
            {createMutation.isError && (
              <div className="mt-2 text-sm text-red-600">
                Error creating app
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}



