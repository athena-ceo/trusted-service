'use client';

import { useState } from 'react';
import { Plus, ChevronUp, ChevronDown, Trash2 } from 'lucide-react';
import { useRuleflowConfig } from '../stores/ruleflow-config-store';
import { PackageConfig } from '../types/ruleflow-config';
import PackageConfigItem from './PackageConfigItem';

const LOCKED_PACKAGE_NAME = 'package_initialisations';

interface PackageConfigListProps {
    selectedPackage?: string | null;
    expandedPackages?: Set<string>;
    onTogglePackageExpanded?: (packageId: string, expanded: boolean) => void;
}

export default function PackageConfigList({
    selectedPackage,
    expandedPackages,
    onTogglePackageExpanded
}: PackageConfigListProps) {
    const DEFAULT_PACKAGE_NAME = 'package_new_package';
    const [showAddDialog, setShowAddDialog] = useState(false);
    const [newPackageName, setNewPackageName] = useState(DEFAULT_PACKAGE_NAME);
    const [newPackageCondition, setNewPackageCondition] = useState('');

    const { config, executeAction } = useRuleflowConfig();

    if (!config) {
        return (
            <div className="flex items-center justify-center h-32 text-gray-500">
                Configuration non chargée
            </div>
        );
    }

    const handleAddPackage = () => {
        if (!newPackageName.trim()) return;

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
        setShowAddDialog(false);
    };

    const handleMovePackage = (packageId: string, direction: 'up' | 'down') => {
        executeAction({
            type: 'MOVE_PACKAGE',
            payload: { id: packageId, direction }
        }, `Déplacement du package ${direction === 'up' ? 'vers le haut' : 'vers le bas'}`);
    };

    const handleDeletePackage = (packageId: string) => {
        const pkg = config.packages.find(p => p.id === packageId);
        if (pkg && window.confirm(`Êtes-vous sûr de vouloir supprimer le package "${pkg.name}" ?`)) {
            executeAction({
                type: 'DELETE_PACKAGE',
                payload: { id: packageId }
            }, `Suppression du package "${pkg.name}"`);
        }
    };

    const sortedPackages = [...config.packages].sort((a, b) => a.execution_order - b.execution_order);
    const firstPackageLocked = sortedPackages[0]?.name === LOCKED_PACKAGE_NAME;

    return (
        <div className="space-y-2">
            {/* Header avec bouton d'ajout */}
            <div className="flex items-center justify-between pb-2 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">
                    Packages ({config.packages.length})
                </h3>
                <button
                    onClick={() => {
                        setNewPackageName(DEFAULT_PACKAGE_NAME);
                        setShowAddDialog(true);
                    }}
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                    <Plus className="w-4 h-4 mr-1" />
                    Ajouter
                </button>
            </div>

            {/* Liste des packages */}
            {sortedPackages.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    <div className="text-4xl mb-2">📦</div>
                    <p>Aucun package défini</p>
                    <button
                        onClick={() => setShowAddDialog(true)}
                        className="mt-2 text-blue-600 hover:text-blue-800 underline"
                    >
                        Créer le premier package
                    </button>
                </div>
            ) : (
                <div className="space-y-2">
                    {sortedPackages.map((pkg, index) => {
                        const isLockedPackage = pkg.name === LOCKED_PACKAGE_NAME;
                        const disableMoveUp = isLockedPackage || index === 0 || (firstPackageLocked && index === 1);
                        const disableMoveDown = isLockedPackage || index === sortedPackages.length - 1;

                        return (
                            <div key={pkg.id} className="relative">
                                {/* Contrôles de déplacement */}
                                <div className="absolute left-1 top-1/2 transform -translate-y-1/2 flex flex-col space-y-1 z-10">
                                    <button
                                        onClick={() => handleMovePackage(pkg.id, 'up')}
                                        disabled={disableMoveUp}
                                        className="p-1 text-gray-400 hover:text-gray-600 disabled:text-gray-300 disabled:cursor-not-allowed"
                                        title="Déplacer vers le haut"
                                    >
                                        <ChevronUp className="w-3 h-3" />
                                    </button>
                                    <button
                                        onClick={() => handleMovePackage(pkg.id, 'down')}
                                        disabled={disableMoveDown}
                                        className="p-1 text-gray-400 hover:text-gray-600 disabled:text-gray-300 disabled:cursor-not-allowed"
                                        title="Déplacer vers le bas"
                                    >
                                        <ChevronDown className="w-3 h-3" />
                                    </button>
                                </div>

                                {/* Bouton de suppression */}
                                <button
                                    onClick={() => handleDeletePackage(pkg.id)}
                                    className="absolute right-1 top-1 p-1 text-gray-400 hover:text-red-600 z-10"
                                    title="Supprimer le package"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>

                                {/* Composant package */}
                                <PackageConfigItem
                                    package={pkg}
                                    isSelected={selectedPackage === pkg.id}
                                    isExpanded={expandedPackages?.has(pkg.id) || false}
                                    onToggleExpanded={(expanded) => onTogglePackageExpanded?.(pkg.id, expanded)}
                                    executionOrder={index + 1}
                                />
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Dialog d'ajout de package */}
            {showAddDialog && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-md">
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
                                    setShowAddDialog(false);
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
        </div>
    );
}
