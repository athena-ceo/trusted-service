'use client';

import ConfigPage from './config-page';

export default function Home() {
  return <ConfigPage />;
}
import { useQuery } from '@tanstack/react-query';
import { RefreshCw, Loader2 } from 'lucide-react';
import axios from 'axios';
import RuntimeSelector from './components/RuntimeSelector';
import AppSelector from './components/AppSelector';
import RuleflowEditor from './components/RuleflowEditor';
import RuleflowDiagram from './components/RuleflowDiagram';
import { RuleflowStructure } from './components/types';

export default function Home() {
  const [selectedRuntime, setSelectedRuntime] = useState<string | null>(null);
  const [selectedApp, setSelectedApp] = useState<string | null>(null);
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const [expandedPackages, setExpandedPackages] = useState<Set<string>>(new Set());

  // Fonction pour gérer la sélection d'un package depuis le diagramme
  const handleSelectPackage = (packageName: string) => {
    setSelectedPackage(packageName);
    // Seul le package sélectionné est étendu, les autres sont collapsés
    setExpandedPackages(new Set([packageName]));
  };

  // Fonction pour basculer l'expansion d'un package
  const handleTogglePackageExpanded = (packageName: string, expanded: boolean) => {
    if (expanded) {
      // Si on étend un package, il devient le seul étendu ET sélectionné
      setSelectedPackage(packageName);
      setExpandedPackages(new Set([packageName]));
    } else {
      // Si on collapse un package, on le désélectionne aussi
      setSelectedPackage(null);
      setExpandedPackages(new Set());
    }
  };

  const { data: structure, isLoading: structureLoading, refetch } = useQuery<RuleflowStructure>({
    queryKey: ['ruleflow-structure', selectedRuntime, selectedApp],
    queryFn: async () => {
      const response = await axios.get(`/api/v1/ruleflow/runtime/${selectedRuntime}/apps/${selectedApp}/structure`);
      return response.data;
    },
    enabled: !!selectedRuntime && !!selectedApp,
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Ruleflow Editor</h1>
              <p className="text-sm text-gray-600 mt-1">
                Edit decision engine ruleflows visually
              </p>
            </div>
            {selectedRuntime && (
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500">Runtime:</span>
                    <button
                      onClick={() => {
                        setSelectedRuntime(null);
                        setSelectedApp(null);
                      }}
                      className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-100 text-blue-800 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors"
                      title="Click to change runtime"
                    >
                      {selectedRuntime}
                      <span className="text-xs opacity-70">✕</span>
                    </button>
                  </div>
                  {selectedApp && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">App:</span>
                      <button
                        onClick={() => setSelectedApp(null)}
                        className="inline-flex items-center gap-2 px-3 py-1.5 bg-green-100 text-green-800 rounded-lg text-sm font-medium hover:bg-green-200 transition-colors"
                        title="Click to change app"
                      >
                        {selectedApp}
                        <span className="text-xs opacity-70">✕</span>
                      </button>
                    </div>
                  )}
                </div>
                {selectedApp && structure && (
                  <div className="flex items-center gap-3 text-xs text-gray-500 border-l border-gray-200 pl-6">
                    <span>Class: <span className="font-mono text-gray-700">{structure.class_name}</span></span>
                    {structureLoading && (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    )}
                    <button
                      onClick={() => refetch()}
                      className="flex items-center gap-1 px-1.5 py-0.5 hover:bg-gray-100 rounded transition-colors"
                      title="Refresh structure"
                    >
                      <RefreshCw className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-full mx-auto px-4 py-6 h-[calc(100vh-120px)]">
        {!selectedRuntime && (
          <div className="max-w-7xl mx-auto">
            <RuntimeSelector
              selected={selectedRuntime}
              onSelect={setSelectedRuntime}
            />
          </div>
        )}

        {selectedRuntime && !selectedApp && (
          <div className="max-w-7xl mx-auto">
            <AppSelector
              runtime={selectedRuntime}
              selected={selectedApp}
              onSelect={setSelectedApp}
            />
          </div>
        )}

        {selectedRuntime && selectedApp && (
          <div className="flex gap-6 h-full">
            {/* Colonne gauche: Ruleflow graphique (1/3) */}
            <div className="w-1/3 bg-white rounded-lg shadow p-4">
              <h3 className="text-lg font-semibold mb-4">Ruleflow Diagram</h3>
              <div className="h-full">
                {structure ? (
                  <RuleflowDiagram
                    packages={structure.packages}
                    selectedPackage={selectedPackage}
                    onSelectPackage={handleSelectPackage}
                  />
                ) : (
                  <div className="h-full bg-gray-50 rounded border-2 border-dashed border-gray-200 flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <Loader2 className="w-8 h-8 mx-auto mb-2 animate-spin" />
                      <p className="text-sm">Loading structure...</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Colonne droite: Edition du package (2/3) */}
            <div className="w-2/3">
              <RuleflowEditor
                runtime={selectedRuntime}
                app={selectedApp}
                selectedPackage={selectedPackage}
                expandedPackages={expandedPackages}
                onTogglePackageExpanded={handleTogglePackageExpanded}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}



