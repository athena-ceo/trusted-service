'use client';

import { useState, useEffect, useRef } from 'react';
import { RefreshCw, Loader2, Save, Play, AlertTriangle } from 'lucide-react';
import RuntimeSelector from './components/RuntimeSelector';
import AppSelector from './components/AppSelector';
import PackageConfigList from './components/PackageConfigList';
import PackageConfigItem from './components/PackageConfigItem';
import { Plus } from 'lucide-react';
import ConfigToolbar from './components/ConfigToolbar';
import RuleflowConfigDiagram from './components/RuleflowConfigDiagram';
import { useRuleflowConfig } from './stores/ruleflow-config-store';

export default function Home() {
    const [selectedRuntime, setSelectedRuntime] = useState<string | null>('runtime');
    const [selectedApp, setSelectedApp] = useState<string | null>('delphes');
    const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
    const [expandedPackages, setExpandedPackages] = useState<Set<string>>(new Set());
    const [showDiagram, setShowDiagram] = useState(true);

    // Gestion des modifications non sauvegardées
    const [showConfirmDialog, setShowConfirmDialog] = useState(false);
    const [pendingAction, setPendingAction] = useState<(() => void) | null>(null);
    const [pendingRuntime, setPendingRuntime] = useState<string | null>(null);
    const [pendingApp, setPendingApp] = useState<string | null>(null);

    const {
        config,
        loadConfig,
        isModified,
        history,
        saveConfig,
        reset,
        executeAction
    } = useRuleflowConfig();

    const DEFAULT_PACKAGE_NAME = 'package_new_package';
    const [showAddPackageDialog, setShowAddPackageDialog] = useState(false);
    const [newPackageName, setNewPackageName] = useState(DEFAULT_PACKAGE_NAME);
    const [newPackageCondition, setNewPackageCondition] = useState('');

    // Charger la configuration quand runtime et app sont sélectionnés
    useEffect(() => {
        if (selectedRuntime && selectedApp) {
            loadConfig(selectedApp, selectedRuntime);
        }
    }, [selectedRuntime, selectedApp, loadConfig]);

    // Gestion des raccourcis clavier pour undo/redo
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && !e.shiftKey && e.key === 'z') {
                e.preventDefault();
                // undo() sera géré par ConfigToolbar
            } else if ((e.metaKey || e.ctrlKey) && (e.shiftKey && e.key === 'z' || e.key === 'y')) {
                e.preventDefault();
                // redo() sera géré par ConfigToolbar
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    // Fonction pour gérer la sélection d'un package depuis le diagramme
    const handleSelectPackage = (packageId: string) => {
        setSelectedPackage(packageId);
        setExpandedPackages(new Set([packageId]));
    };

    // Fonction pour basculer l'expansion d'un package
    const handleTogglePackageExpanded = (packageId: string, expanded: boolean) => {
        if (expanded) {
            setSelectedPackage(packageId);
            setExpandedPackages(new Set([packageId]));
        } else {
            setSelectedPackage(null);
            setExpandedPackages(new Set());
        }
    };

    // Fonction pour gérer le changement de runtime avec vérification des modifications
    const handleRuntimeChange = (newRuntime: string | null) => {
        if (isModified && (selectedRuntime !== null || selectedApp !== null)) {
            setPendingRuntime(newRuntime);
            setPendingApp(null); // Changer de runtime réinitialise aussi l'app
            setShowConfirmDialog(true);
            setPendingAction(() => () => {
                // Action à exécuter après confirmation
                if (newRuntime) {
                    setSelectedRuntime(newRuntime);
                    setSelectedApp(null);
                } else {
                    setSelectedRuntime(null);
                    setSelectedApp(null);
                }
                reset();
            });
        } else {
            // Pas de modifications, on peut changer directement
            if (newRuntime) {
                setSelectedRuntime(newRuntime);
                setSelectedApp(null);
            } else {
                setSelectedRuntime(null);
                setSelectedApp(null);
            }
            if (!newRuntime) {
                reset();
            }
        }
    };

    // Fonction pour gérer le changement d'app avec vérification des modifications
    const handleAppChange = (newApp: string | null) => {
        if (isModified && selectedApp !== null) {
            setPendingApp(newApp);
            setShowConfirmDialog(true);
            setPendingAction(() => () => {
                // Action à exécuter après confirmation
                setSelectedApp(newApp);
                if (!newApp) {
                    reset();
                }
            });
        } else {
            // Pas de modifications, on peut changer directement
            setSelectedApp(newApp);
            if (!newApp) {
                reset();
            }
        }
    };

    // Gestion de la confirmation du dialogue
    const handleConfirm = async () => {
        if (pendingAction) {
            // Sauvegarder d'abord si l'utilisateur confirme
            try {
                await saveConfig('Sauvegarde avant changement de contexte');
            } catch (error) {
                console.error('Erreur lors de la sauvegarde:', error);
                // Continuer quand même le changement
            }
            pendingAction();
            setPendingAction(null);
            setPendingRuntime(null);
            setPendingApp(null);
        }
        setShowConfirmDialog(false);
    };

    // Gestion de l'annulation du dialogue
    const handleCancel = () => {
        setShowConfirmDialog(false);
        setPendingAction(null);
        setPendingRuntime(null);
        setPendingApp(null);
    };

    // Gestion de l'ignorance des modifications
    const handleDiscard = () => {
        if (pendingAction) {
            pendingAction();
            setPendingAction(null);
            setPendingRuntime(null);
            setPendingApp(null);
        }
        setShowConfirmDialog(false);
    };

    // Gestion de l'ajout de package
    const handleAddPackage = () => {
        if (!newPackageName.trim() || !config) return;

        let insertIndex = config.packages.length;
        if (selectedPackage) {
            const currentIndex = config.packages.findIndex(pkg => pkg.id === selectedPackage);
            if (currentIndex !== -1) {
                insertIndex = currentIndex + 1;
            }
        }

        executeAction({
            type: 'ADD_PACKAGE',
            payload: {
                package: {
                    name: newPackageName.trim(),
                    condition: newPackageCondition.trim() || null,
                    execution_order: insertIndex,
                    rules: []
                },
                insertIndex
            }
        }, `Ajout du package "${newPackageName}"`);

        setNewPackageName(DEFAULT_PACKAGE_NAME);
        setNewPackageCondition('');
        setShowAddPackageDialog(false);
    };

    const handleReorderPackage = (packageId: string, newIndex: number) => {
        executeAction({
            type: 'REORDER_PACKAGE',
            payload: { id: packageId, newIndex }
        }, 'Réorganisation des packages via le diagramme');
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* Header principal */}
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">Ruleflow Configuration</h1>
                            <p className="text-sm text-gray-600 mt-1">
                                Ruleflow and decision engine configuration
                            </p>
                        </div>

                        {/* Indicateurs de statut */}
                        {config && (
                            <div className="flex items-center gap-4 text-sm">
                                <div className="flex items-center gap-2">
                                    <div className={`w-2 h-2 rounded-full ${isModified ? 'bg-yellow-500' : 'bg-green-500'}`} />
                                    <span className="text-gray-600">
                                        {isModified ? 'Modifié' : 'Sauvegardé'}
                                    </span>
                                </div>

                                <div className="text-gray-500">
                                    Version {history.currentIndex + 1}/{history.versions.length}
                                </div>

                            </div>
                        )}
                    </div>
                </div>
            </header>

            {/* Barre d'outils de configuration */}
            {config && <ConfigToolbar />}

            {/* Contenu principal */}
            <div className="flex-1 flex">
                {/* Panel de gauche - Sélection runtime/app + Diagramme */}
                <div className="w-130 bg-white border-r border-gray-200 flex flex-col">
                    <div className="p-4 border-b border-gray-200">
                        <h2 className="text-lg font-medium text-gray-900 mb-4">Configuration</h2>

                        <div className="space-y-4">
                            {/* Sélection du runtime */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Runtime Environment
                                </label>
                                {!selectedRuntime ? (
                                    <RuntimeSelector
                                        selected={null}
                                        onSelect={handleRuntimeChange}
                                    />
                                ) : (
                                    <div className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg">
                                        <span className="text-sm font-medium text-blue-900">
                                            {selectedRuntime}
                                        </span>
                                        <button
                                            onClick={() => handleRuntimeChange(null)}
                                            className="text-blue-600 hover:text-blue-800"
                                        >
                                            Changer
                                        </button>
                                    </div>
                                )}
                            </div>

                            {/* Sélection de l'app */}
                            {selectedRuntime && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Application
                                    </label>
                                    {!selectedApp ? (
                                        <AppSelector
                                            runtime={selectedRuntime}
                                            selected={null}
                                            onSelect={handleAppChange}
                                        />
                                    ) : (
                                        <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
                                            <span className="text-sm font-medium text-green-900">
                                                {selectedApp}
                                            </span>
                                            <button
                                                onClick={() => handleAppChange(null)}
                                                className="text-green-600 hover:text-green-800"
                                            >
                                                Changer
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Diagramme de flux (si une configuration est chargée) */}
                    {config && showDiagram && (
                        <div className="flex-1 overflow-auto border-t border-gray-200">
                            <div className="p-4">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-lg font-medium text-gray-900">
                                        Ruleflow diagram
                                    </h3>
                                </div>
                                <div className="text-sm text-gray-500 mb-4">
                                    {config.packages.length} package{config.packages.length !== 1 ? 's' : ''} • {' '}
                                    {config.packages.reduce((total, pkg) => total + pkg.rules.length, 0)} règle{config.packages.reduce((total, pkg) => total + pkg.rules.length, 0) !== 1 ? 's' : ''}
                                </div>
                                <RuleflowConfigDiagram
                                    packages={config.packages}
                                    selectedPackage={selectedPackage}
                                    onSelectPackage={handleSelectPackage}
                                    onReorderPackage={handleReorderPackage}
                                />
                            </div>
                        </div>
                    )}
                </div>

                {/* Panel principal - Éditeur de package */}
                <div className="flex-1 flex flex-col bg-gray-50">
                    {config ? (
                        config.packages.length === 0 ? (
                            <div className="flex-1 flex items-center justify-center">
                                <div className="text-center">
                                    <div className="text-6xl mb-4">🔧</div>
                                    <h3 className="text-xl font-medium text-gray-900 mb-2">
                                        Configuration vide
                                    </h3>
                                    <p className="text-gray-600 mb-4">
                                        Commencez par ajouter un package pour structurer votre ruleflow.
                                    </p>
                                </div>
                            </div>
                        ) : selectedPackage ? (
                            <div className="flex-1 flex flex-col bg-white">
                                <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                                    <div>
                                        <h2 className="text-2xl font-bold text-gray-900">
                                            Éditeur de package
                                        </h2>
                                        <p className="text-sm text-gray-600 mt-1">
                                            {config.packages.find(p => p.id === selectedPackage)?.name || selectedPackage}
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => {
                                            setNewPackageName(DEFAULT_PACKAGE_NAME);
                                            setShowAddPackageDialog(true);
                                        }}
                                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                                    >
                                        <Plus className="w-4 h-4 mr-2" />
                                        Add package
                                    </button>
                                </div>
                                <div className="flex-1 overflow-auto p-6">
                                    {(() => {
                                        const selectedPkg = config.packages.find(p => p.id === selectedPackage);
                                        if (!selectedPkg) {
                                            return (
                                                <div className="text-center py-12 text-gray-500">
                                                    Package introuvable
                                                </div>
                                            );
                                        }
                                        return (
                                            <PackageConfigItem
                                                package={selectedPkg}
                                                isSelected={true}
                                                isExpanded={expandedPackages?.has(selectedPackage) || false}
                                                onToggleExpanded={(expanded) => handleTogglePackageExpanded(selectedPackage, expanded)}
                                                executionOrder={selectedPkg.execution_order + 1}
                                            />
                                        );
                                    })()}
                                </div>
                            </div>
                        ) : (
                            <div className="flex-1 flex items-center justify-center">
                                <div className="text-center">
                                    <div className="text-6xl mb-4">📦</div>
                                    <h3 className="text-xl font-medium text-gray-900 mb-2">
                                        Sélectionnez un package
                                    </h3>
                                    <p className="text-gray-600 mb-4">
                                        Cliquez sur un package dans le diagramme pour commencer l'édition.
                                    </p>
                                    <div className="text-sm text-gray-500">
                                        💡 Tip: Utilisez Ctrl/Cmd+Z et Ctrl/Cmd+Y pour annuler et rétablir vos modifications
                                    </div>
                                </div>
                            </div>
                        )
                    ) : (
                        <div className="flex-1 flex items-center justify-center">
                            {selectedRuntime && selectedApp ? (
                                <div className="text-center">
                                    <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
                                    <p className="text-gray-600">Chargement de la configuration...</p>
                                </div>
                            ) : (
                                <div className="text-center">
                                    <div className="text-6xl mb-4">🚀</div>
                                    <h3 className="text-xl font-medium text-gray-900 mb-2">
                                        Bienvenue dans l'éditeur Ruleflow
                                    </h3>
                                    <p className="text-gray-600">
                                        Sélectionnez un runtime et une application pour commencer l'édition.
                                    </p>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Dialog d'ajout de package */}
            {showAddPackageDialog && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">
                            Nouveau Package
                        </h3>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Nom du package *
                                </label>
                                <input
                                    type="text"
                                    value={newPackageName}
                                    onChange={(e) => setNewPackageName(e.target.value)}
                                    placeholder="ex: package_validation"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    autoFocus
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Condition (optionelle)
                                </label>
                                <input
                                    type="text"
                                    value={newPackageCondition}
                                    onChange={(e) => setNewPackageCondition(e.target.value)}
                                    placeholder="ex: input.intention_id.startswith('VAL_')"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    Expression Python évaluée pour déterminer si le package doit être exécuté
                                </p>
                            </div>
                        </div>

                        <div className="flex justify-end space-x-3 mt-6">
                            <button
                                onClick={() => {
                                    setShowAddPackageDialog(false);
                                    setNewPackageName(DEFAULT_PACKAGE_NAME);
                                    setNewPackageCondition('');
                                }}
                                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                            >
                                Annuler
                            </button>
                            <button
                                onClick={handleAddPackage}
                                disabled={!newPackageName.trim()}
                                className="px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-md"
                            >
                                Ajouter
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Dialogue de confirmation pour les modifications non sauvegardées */}
            {showConfirmDialog && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg shadow-xl max-w-md w-full border-2 border-yellow-200">
                        <div className="bg-yellow-50 p-4 border-b border-yellow-200">
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="w-6 h-6 text-yellow-600" />
                                <h3 className="text-lg font-semibold text-gray-900">Modifications non sauvegardées</h3>
                            </div>
                        </div>

                        <div className="p-6">
                            <p className="text-gray-700 mb-6">
                                {pendingRuntime !== null
                                    ? `Vous avez des modifications non sauvegardées. Que souhaitez-vous faire avant de changer de runtime ?`
                                    : `Vous avez des modifications non sauvegardées. Que souhaitez-vous faire avant de changer d'application ?`}
                            </p>

                            <div className="flex justify-end gap-3">
                                <button
                                    onClick={handleCancel}
                                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                                >
                                    Annuler
                                </button>
                                <button
                                    onClick={handleDiscard}
                                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                                >
                                    Ignorer les modifications
                                </button>
                                <button
                                    onClick={handleConfirm}
                                    className="px-4 py-2 text-white bg-yellow-600 rounded-md hover:bg-yellow-700 transition-colors"
                                >
                                    Sauvegarder et continuer
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
