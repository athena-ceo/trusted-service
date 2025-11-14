'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import axios from 'axios';
import PackageItem from './PackageItem';
import { Package as PackageType } from './types';

interface PackageListProps {
  runtime: string;
  app: string;
  packages: PackageType[];
  selectedPackage?: string | null;
  expandedPackages?: Set<string>;
  onTogglePackageExpanded?: (packageName: string, expanded: boolean) => void;
}

export default function PackageList({ runtime, app, packages, selectedPackage, expandedPackages, onTogglePackageExpanded }: PackageListProps) {
  const DEFAULT_PACKAGE_NAME = 'package_new_package';
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newPackageName, setNewPackageName] = useState(DEFAULT_PACKAGE_NAME);
  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: async (packageName: string) => {
      const response = await axios.delete(
        `/api/v1/ruleflow/runtime/${runtime}/apps/${app}/package/${packageName}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ruleflow-structure', runtime, app] });
    },
  });

  const moveMutation = useMutation({
    mutationFn: async ({ packageName, direction }: { packageName: string; direction: string }) => {
      const response = await axios.post(
        `/api/v1/ruleflow/runtime/${runtime}/apps/${app}/package/move`,
        { direction },
        { params: { package_name: packageName } }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ruleflow-structure', runtime, app] });
    },
  });

  const addMutation = useMutation({
    mutationFn: async ({ name, executionOrder }: { name: string; executionOrder: number }) => {
      console.log('Adding package:', { name: `package_${name}`, executionOrder, runtime, app });
      const response = await axios.post(
        `/api/v1/ruleflow/runtime/${runtime}/apps/${app}/package/add`,
        {
          name: `package_${name}`,
          condition: null,
          execution_order: executionOrder,
        }
      );
      console.log('Package add response:', response.data);
      return response.data;
    },
    onSuccess: (data, variables) => {
      console.log('Package added successfully:', data);
      queryClient.invalidateQueries({ queryKey: ['ruleflow-structure', runtime, app] });
      // Sélectionner automatiquement le nouveau package créé
      if (onTogglePackageExpanded) {
        const newPackageName = `package_${variables.name}`;
        onTogglePackageExpanded(newPackageName, true);
      }
      setNewPackageName(DEFAULT_PACKAGE_NAME);
      setShowAddDialog(false);
    },
    onError: (error) => {
      console.error('Error adding package:', error);
      // Afficher l'erreur à l'utilisateur
      alert(`Error adding package: ${error.message}`);
    },
  });

  const handleMove = (packageName: string, direction: 'up' | 'down') => {
    moveMutation.mutate({ packageName, direction });
  };

  const handleDelete = (packageName: string) => {
    if (confirm(`Are you sure you want to delete package ${packageName}?`)) {
      deleteMutation.mutate(packageName);
    }
  };

  const handleAdd = () => {
    if (!newPackageName.trim()) return;

    // Déterminer la position d'insertion : juste après le package sélectionné
    let executionOrder = packages.length; // Par défaut à la fin

    if (selectedPackage) {
      const selectedIndex = packages.findIndex((pkg) => pkg.name === selectedPackage);
      if (selectedIndex !== -1) {
        executionOrder = selectedIndex + 1;
      }
    }

    addMutation.mutate({
      name: newPackageName.trim(),
      executionOrder: executionOrder,
    });
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Packages</h2>
        <button
          onClick={() => {
            setNewPackageName(DEFAULT_PACKAGE_NAME);
            setShowAddDialog(true);
          }}
          className="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Package
        </button>
      </div>

      <div className="space-y-3">
        {packages.map((pkg, index) => (
          <PackageItem
            key={pkg.name}
            runtime={runtime}
            app={app}
            package={pkg}
            index={index}
            total={packages.length}
            onMove={handleMove}
            onDelete={handleDelete}
            isSelected={selectedPackage === pkg.name}
            isExpanded={expandedPackages?.has(pkg.name)}
            onToggleExpanded={onTogglePackageExpanded}
          />
        ))}
      </div>

      {showAddDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Add New Package</h3>
            <input
              type="text"
              value={newPackageName}
              onChange={(e) => setNewPackageName(e.target.value)}
              placeholder="package_name (without 'package_' prefix)"
              className="w-full px-3 py-2 border rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
              autoFocus
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => {
                  setShowAddDialog(false);
                  setNewPackageName(DEFAULT_PACKAGE_NAME);
                }}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
                disabled={addMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={handleAdd}
                disabled={addMutation.isPending || !newPackageName.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {addMutation.isPending ? 'Adding...' : 'Add'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

