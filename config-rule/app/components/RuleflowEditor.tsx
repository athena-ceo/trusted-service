'use client';

import { useQuery } from '@tanstack/react-query';
import { Loader2, RefreshCw } from 'lucide-react';
import axios from 'axios';
import PackageList from './PackageList';
import { RuleflowStructure } from './types';

interface RuleflowEditorProps {
  runtime: string;
  app: string;
  selectedPackage?: string | null;
  expandedPackages?: Set<string>;
  onTogglePackageExpanded?: (packageName: string, expanded: boolean) => void;
}

export default function RuleflowEditor({ runtime, app, selectedPackage, expandedPackages, onTogglePackageExpanded }: RuleflowEditorProps) {
  const { data: structure, isLoading, error, refetch } = useQuery<RuleflowStructure>({
    queryKey: ['ruleflow-structure', runtime, app],
    queryFn: async () => {
      console.log('Fetching ruleflow structure for:', { runtime, app });
      const response = await axios.get(`/api/v1/ruleflow/runtime/${runtime}/apps/${app}/structure`);
      console.log('Ruleflow structure response:', response.data);
      return response.data;
    },
    enabled: !!runtime && !!app,
    retry: (failureCount, error) => {
      console.error('Query failed:', { failureCount, error });
      return failureCount < 3;
    },
  });

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center h-full flex items-center justify-center">
        <div>
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-gray-400" />
          <p className="mt-4 text-gray-600">Loading ruleflow structure...</p>
        </div>
      </div>
    );
  }

  if (error) {
    console.error('Error in RuleflowEditor:', error);
    return (
      <div className="bg-white rounded-lg shadow p-8 h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            Error loading ruleflow structure: {error.message}
          </div>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!structure) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center h-full flex items-center justify-center">
        <p className="text-gray-600">No ruleflow structure found</p>
      </div>
    );
  }

  return (
    <div className="h-full">
      <PackageList
        runtime={runtime}
        app={app}
        packages={structure.packages}
        selectedPackage={selectedPackage}
        expandedPackages={expandedPackages}
        onTogglePackageExpanded={onTogglePackageExpanded}
      />
    </div>
  );
}



