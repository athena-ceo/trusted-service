'use client';

import { useEffect, useState } from 'react';
import { ChevronDown, ChevronRight, Code, Plus, Trash2, ChevronUp, ChevronDown as RuleDown, Settings } from 'lucide-react';
import { useRuleflowConfig } from '../stores/ruleflow-config-store';
import { PackageConfig, RuleConfig } from '../types/ruleflow-config';
import AdvancedRuleEditorV2 from './AdvancedRuleEditorV2';

interface PackageConfigItemProps {
    package: PackageConfig;
    isSelected: boolean;
    isExpanded: boolean;
    onToggleExpanded: (expanded: boolean) => void;
    executionOrder: number;
}

const DEFAULT_RULE_NAME = 'rule_new_rule';

const formatRuleDisplayName = (name: string): string => {
    if (!name) return '';
    const withoutPrefix = name.startsWith('rule_') ? name.slice(5) : name;
    if (!withoutPrefix) return name;
    const withSpaces = withoutPrefix.replace(/_/g, ' ');
    return withSpaces.charAt(0).toUpperCase() + withSpaces.slice(1);
};

// Fonction pour simplifier l'affichage de la condition
const simplifyCondition = (condition: string | null): string => {
    if (!condition) return '';
    
    // Pattern pour extraire: input.field_values["key"] == "value" ou input.field_values['key'] == 'value'
    const pattern1 = /input\.field_values\[["']([^"']+)["']\]\s*==\s*["']([^"']+)["']/;
    const match1 = condition.match(pattern1);
    if (match1) {
        return `${match1[1]} = ${match1[2]}`;
    }
    
    // Pattern pour: input.field_values["key"] == value (sans guillemets pour la valeur)
    const pattern2 = /input\.field_values\[["']([^"']+)["']\]\s*==\s*([^\s\)]+)/;
    const match2 = condition.match(pattern2);
    if (match2) {
        return `${match2[1]} = ${match2[2]}`;
    }
    
    // Si aucun pattern ne correspond, retourner la condition telle quelle
    return condition;
};

export default function PackageConfigItem({
    package: pkg,
    isSelected,
    isExpanded,
    onToggleExpanded,
    executionOrder
}: PackageConfigItemProps) {
    const [showAddRuleDialog, setShowAddRuleDialog] = useState(false);
    const [newRuleName, setNewRuleName] = useState(DEFAULT_RULE_NAME);
    const [editingPackage, setEditingPackage] = useState(false);
    const [packageName, setPackageName] = useState(pkg.name);
    const [packageCondition, setPackageCondition] = useState(pkg.condition || '');
    const [editingRuleAdvanced, setEditingRuleAdvanced] = useState<string | null>(null);

    const { executeAction } = useRuleflowConfig();

    // Synchroniser le formulaire local lorsque l'on change de package
    useEffect(() => {
        setPackageName(pkg.name);
        setPackageCondition(pkg.condition || '');
        setEditingPackage(false);
    }, [pkg.id, pkg.name, pkg.condition]);

    const handlePackageUpdate = () => {
        if (packageName.trim() !== pkg.name || (packageCondition.trim() || null) !== pkg.condition) {
            executeAction({
                type: 'UPDATE_PACKAGE',
                payload: {
                    id: pkg.id,
                    updates: {
                        name: packageName.trim(),
                        condition: packageCondition.trim() || null
                    }
                }
            }, `Modification du package "${pkg.name}"`);
        }
        setEditingPackage(false);
    };

    const handleAddRule = () => {
        const finalName = newRuleName.trim() || DEFAULT_RULE_NAME;
        const ruleCode = `output.details.append("${finalName}")\n# TODO: Implémenter la logique de la règle`;

        executeAction({
            type: 'ADD_RULE',
            payload: {
                packageId: pkg.id,
                rule: {
                    name: finalName,
                    code: ruleCode,
                    condition: null
                }
            }
        }, `Ajout de la règle "${finalName}" au package "${pkg.name}"`);

        setNewRuleName(DEFAULT_RULE_NAME);
        setShowAddRuleDialog(false);
    };

    const handleMoveRule = (ruleId: string, direction: 'up' | 'down') => {
        const rule = pkg.rules.find(r => r.id === ruleId);
        executeAction({
            type: 'MOVE_RULE',
            payload: {
                packageId: pkg.id,
                ruleId,
                direction
            }
        }, `Déplacement de la règle "${rule?.name}" ${direction === 'up' ? 'vers le haut' : 'vers le bas'}`);
    };

    const handleDeleteRule = (ruleId: string) => {
        const rule = pkg.rules.find(r => r.id === ruleId);
        if (rule && window.confirm(`Êtes-vous sûr de vouloir supprimer la règle "${rule.name}" ?`)) {
            executeAction({
                type: 'DELETE_RULE',
                payload: { packageId: pkg.id, ruleId }
            }, `Suppression de la règle "${rule.name}"`);
        }
    };

    const handleUpdateRule = (ruleId: string, updates: Partial<RuleConfig>) => {
        const rule = pkg.rules.find(r => r.id === ruleId);
        executeAction({
            type: 'UPDATE_RULE',
            payload: { packageId: pkg.id, ruleId, updates }
        }, `Modification de la règle "${rule?.name}"`);
    };

    const handleAdvancedRuleSave = (updatedRule: RuleConfig) => {
        handleUpdateRule(updatedRule.id, updatedRule);
        setEditingRuleAdvanced(null);
    };

    const ruleBeingEdited = editingRuleAdvanced
        ? pkg.rules.find(r => r.id === editingRuleAdvanced)
        : null;

    return (
        <div className={`border rounded-lg ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'} ml-8`}>
            {/* En-tête du package */}
            <div className="p-3 border-b border-gray-200 last:border-b-0">
                <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center space-x-2 flex-1 min-w-0">
                        {/* Bouton d'expansion */}
                        <button
                            onClick={() => onToggleExpanded(!isExpanded)}
                            className="text-gray-500 hover:text-gray-700"
                        >
                            {isExpanded ? (
                                <ChevronDown className="w-4 h-4" />
                            ) : (
                                <ChevronRight className="w-4 h-4" />
                            )}
                        </button>

                        {/* Numéro d'ordre */}
                        <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded">
                            {executionOrder}
                        </span>

                        {/* Nom du package */}
                        {editingPackage ? (
                            <input
                                type="text"
                                value={packageName}
                                onChange={(e) => setPackageName(e.target.value)}
                                onBlur={handlePackageUpdate}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') handlePackageUpdate();
                                    if (e.key === 'Escape') {
                                        setPackageName(pkg.name);
                                        setPackageCondition(pkg.condition || '');
                                        setEditingPackage(false);
                                    }
                                }}
                                className="px-2 py-1 border border-blue-300 rounded text-sm font-medium"
                                autoFocus
                            />
                        ) : (
                            <button
                                onClick={() => setEditingPackage(true)}
                                className="text-sm font-medium text-gray-900 hover:text-blue-600 text-left"
                            >
                                {pkg.name}
                            </button>
                        )}

                    </div>

                    {/* Actions du package */}
                    <div className="flex items-center space-x-1 shrink-0">
                        <span className="text-xs text-gray-500">
                            {pkg.rules.length} règle{pkg.rules.length !== 1 ? 's' : ''}
                        </span>

                        <button
                            onClick={() => {
                                setNewRuleName(DEFAULT_RULE_NAME);
                                setShowAddRuleDialog(true);
                            }}
                            className="p-1 text-gray-400 hover:text-blue-600"
                            title="Ajouter une règle"
                        >
                            <Plus className="w-4 h-4" />
                        </button>
                    </div>
                </div>
                
                {/* Condition du package affichée sous le nom */}
                <div className="mt-2 ml-8">
                    {editingPackage ? (
                        <input
                            type="text"
                            value={packageCondition}
                            onChange={(e) => setPackageCondition(e.target.value)}
                            onBlur={handlePackageUpdate}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') handlePackageUpdate();
                                if (e.key === 'Escape') {
                                    setPackageCondition(pkg.condition || '');
                                    setEditingPackage(false);
                                }
                            }}
                            placeholder="Condition (ex: input.field_values['departement'] == '78')"
                            className="w-full px-2 py-1 border border-blue-300 rounded text-xs font-mono"
                            autoFocus
                        />
                    ) : (
                        <button
                            onClick={() => {
                                setEditingPackage(true);
                                setPackageCondition(pkg.condition || '');
                            }}
                            className={`text-xs px-2 py-1 rounded text-left w-full ${
                                pkg.condition 
                                    ? 'text-blue-600 bg-blue-50 hover:bg-blue-100 border border-blue-200' 
                                    : 'text-gray-500 bg-gray-50 hover:bg-gray-100 border border-gray-200'
                            }`}
                            title={pkg.condition ? "Cliquer pour modifier la condition" : "Cliquer pour ajouter une condition"}
                        >
                            {pkg.condition ? (
                                <span className="font-mono">if {simplifyCondition(pkg.condition)}</span>
                            ) : (
                                <span className="italic">+ Ajouter une condition</span>
                            )}
                        </button>
                    )}
                </div>
            </div>

            {/* Liste des règles (si étendu) */}
            {isExpanded && (
                <div className="p-3 space-y-2">
                    {pkg.rules.length === 0 ? (
                        <div className="text-center py-4 text-gray-500">
                            <Code className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                            <p className="text-sm">Aucune règle définie</p>
                            <button
                                onClick={() => {
                                    setNewRuleName(DEFAULT_RULE_NAME);
                                    setShowAddRuleDialog(true);
                                }}
                                className="mt-1 text-xs text-blue-600 hover:text-blue-800 underline"
                            >
                                Ajouter la première règle
                            </button>
                        </div>
                    ) : (
                        pkg.rules.map((rule, ruleIndex) => (
                            <div key={rule.id} className="relative border border-gray-100 rounded p-2 hover:border-gray-200">
                                {/* Contrôles de déplacement des règles */}
                                <div className="absolute left-1 top-1/2 transform -translate-y-1/2 flex flex-col space-y-1">
                                    <button
                                        onClick={() => handleMoveRule(rule.id, 'up')}
                                        disabled={ruleIndex === 0}
                                        className="p-0.5 text-gray-300 hover:text-gray-500 disabled:text-gray-200"
                                        title="Déplacer vers le haut"
                                    >
                                        <ChevronUp className="w-3 h-3" />
                                    </button>
                                    <button
                                        onClick={() => handleMoveRule(rule.id, 'down')}
                                        disabled={ruleIndex === pkg.rules.length - 1}
                                        className="p-0.5 text-gray-300 hover:text-gray-500 disabled:text-gray-200"
                                        title="Déplacer vers le bas"
                                    >
                                        <RuleDown className="w-3 h-3" />
                                    </button>
                                </div>

                                {/* Boutons d'action de la règle */}
                                <div className="absolute right-1 top-1 flex space-x-1">
                                    <button
                                        onClick={() => setEditingRuleAdvanced(rule.id)}
                                        className="p-0.5 text-gray-300 hover:text-blue-500"
                                        title="Édition avancée"
                                    >
                                        <Settings className="w-3 h-3" />
                                    </button>
                                    <button
                                        onClick={() => handleDeleteRule(rule.id)}
                                        className="p-0.5 text-gray-300 hover:text-red-500"
                                        title="Supprimer la règle"
                                    >
                                        <Trash2 className="w-3 h-3" />
                                    </button>
                                </div>

                                {/* Contenu de la règle */}
                                <div className="ml-6 mr-6">
                                    <div className="flex items-center space-x-2 mb-1">
                                        <span className="text-xs font-medium text-gray-700">
                                            {formatRuleDisplayName(rule.name)}
                                        </span>
                                        {rule.condition && (
                                            <span className="text-xs text-orange-600 bg-orange-100 px-1 py-0.5 rounded">
                                                if {rule.condition}
                                            </span>
                                        )}
                                    </div>

                                    {/* Condition de la règle */}
                                    <input
                                        type="text"
                                        value={rule.condition || ''}
                                        onChange={(e) => handleUpdateRule(rule.id, { condition: e.target.value || null })}
                                        placeholder="Condition de la règle (optionnelle)"
                                        className="w-full mb-2 px-2 py-1 text-xs border border-gray-200 rounded"
                                    />

                                    <textarea
                                        value={rule.code}
                                        onChange={(e) => handleUpdateRule(rule.id, { code: e.target.value })}
                                        className="w-full text-xs font-mono bg-gray-50 border border-gray-200 rounded p-2 resize-y"
                                        placeholder="Code Python de la règle..."
                                        rows={7}
                                    />
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* Dialog d'ajout de règle */}
            {showAddRuleDialog && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-md">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">
                            Nouvelle Règle pour "{pkg.name}"
                        </h3>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Nom de la règle *
                            </label>
                            <input
                                type="text"
                                value={newRuleName}
                                onChange={(e) => setNewRuleName(e.target.value)}
                                placeholder="ex: rule_validation_email"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                autoFocus
                            />
                        </div>

                        <div className="flex justify-end space-x-3 mt-6">
                            <button
                                onClick={() => {
                                    setShowAddRuleDialog(false);
                                    setNewRuleName(DEFAULT_RULE_NAME);
                                }}
                                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                            >
                                Annuler
                            </button>
                            <button
                                onClick={handleAddRule}
                                disabled={!newRuleName.trim()}
                                className="px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-md"
                            >
                                Ajouter
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Modal d'édition avancée */}
            {editingRuleAdvanced && ruleBeingEdited && (
                <AdvancedRuleEditorV2
                    rule={ruleBeingEdited}
                    onSave={handleAdvancedRuleSave}
                    onCancel={() => setEditingRuleAdvanced(null)}
                />
            )}
        </div>
    );
}
