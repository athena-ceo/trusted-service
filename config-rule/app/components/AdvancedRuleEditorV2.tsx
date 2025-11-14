'use client';

import { useState } from 'react';
import { Code2, Settings, Eye, EyeOff, Save, X, Plus, Trash2 } from 'lucide-react';
import { RuleConfig, OutputAssignment } from '../types/ruleflow-config';

interface AdvancedRuleEditorProps {
    rule: RuleConfig;
    onSave: (updatedRule: RuleConfig) => void;
    onCancel: () => void;
}

// Structure des paramètres output selon le modèle Pydantic
interface OutputParameterDefinition {
    name: string;
    type: 'dropdown' | 'string' | 'list';
    options?: string[];
    description: string;
}

const OUTPUT_PARAMETERS: OutputParameterDefinition[] = [
    {
        name: 'handling',
        type: 'dropdown',
        options: ['AUTOMATED', 'AGENT', 'DEFLECTION'],
        description: 'Mode de traitement du cas'
    },
    {
        name: 'acknowledgement_to_requester',
        type: 'string',
        description: 'Accusé de réception à envoyer au demandeur'
    },
    {
        name: 'response_template_id',
        type: 'dropdown',
        options: ['response_template_id_api_a_renouveler', 'response_template_id_atda', 'response_template_id_dublin', 'response_template_id_sauf_conduits'],
        description: 'ID du template de réponse'
    },
    {
        name: 'work_basket',
        type: 'dropdown',
        options: ['work_basket_accueil', 'work_basket_pref_etrangers_aes_salarie', 'work_basket_api_a_renouveler', 'work_basket_asile_priorite', 'work_basket_atda', 'work_basket_generique', 'work_basket_dublin', 'work_basket_reorientation', 'work_basket_sauf_conduits', 'work_basket_ukraine'],
        description: 'Panier de travail de destination'
    },
    {
        name: 'priority',
        type: 'dropdown',
        options: ['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'],
        description: 'Niveau de priorité du cas'
    },
    {
        name: 'notes',
        type: 'list',
        description: 'Notes additionnelles (liste)'
    },
    {
        name: 'details',
        type: 'list',
        description: 'Détails de traçage (liste)'
    }
];

// Type pour les valeurs des paramètres output
interface OutputParameterValue {
    parameter: string;
    value: string | string[];
    enabled: boolean;
}

export default function AdvancedRuleEditorV2({ rule, onSave, onCancel }: AdvancedRuleEditorProps) {
    const [activeTab, setActiveTab] = useState<'initialization' | 'output-params'>('initialization');
    const [initializationCode, setInitializationCode] = useState(rule.freeCode || '');

    // Initialiser les paramètres output à partir de outputAssignments existantes
    const [outputParams, setOutputParams] = useState<OutputParameterValue[]>(() => {
        return OUTPUT_PARAMETERS.map(param => {
            const existing = (rule.outputAssignments || []).find(a => a.attribute === param.name);

            if (param.type === 'list') {
                // Pour les listes, regrouper toutes les affectations de type .append
                const listItems = (rule.outputAssignments || [])
                    .filter(a => a.attribute.startsWith(`${param.name}.append`))
                    .map(a => a.value);

                return {
                    parameter: param.name,
                    value: listItems.length > 0 ? listItems : [''],
                    enabled: listItems.length > 0
                };
            } else {
                return {
                    parameter: param.name,
                    value: existing ? existing.value : '',
                    enabled: !!existing
                };
            }
        });
    });

    const [showPreview, setShowPreview] = useState(false);

    const handleToggleParameter = (paramName: string) => {
        setOutputParams(prev => prev.map(param =>
            param.parameter === paramName
                ? { ...param, enabled: !param.enabled }
                : param
        ));
    };

    const handleUpdateParameterValue = (paramName: string, value: string | string[]) => {
        setOutputParams(prev => prev.map(param =>
            param.parameter === paramName
                ? { ...param, value }
                : param
        ));
    };

    const handleAddListItem = (paramName: string) => {
        setOutputParams(prev => prev.map(param =>
            param.parameter === paramName && Array.isArray(param.value)
                ? { ...param, value: [...param.value, ''] }
                : param
        ));
    };

    const handleRemoveListItem = (paramName: string, index: number) => {
        setOutputParams(prev => prev.map(param =>
            param.parameter === paramName && Array.isArray(param.value)
                ? { ...param, value: param.value.filter((_, i) => i !== index) }
                : param
        ));
    };

    const handleUpdateListItem = (paramName: string, index: number, value: string) => {
        setOutputParams(prev => prev.map(param =>
            param.parameter === paramName && Array.isArray(param.value)
                ? {
                    ...param,
                    value: param.value.map((item, i) => i === index ? value : item)
                }
                : param
        ));
    };

    const generateCombinedCode = () => {
        const lines = [];
        lines.push(`def ${rule.name}(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):`);

        // Code d'initialisation
        if (initializationCode.trim()) {
            const initLines = initializationCode.split('\n');
            initLines.forEach(line => {
                lines.push(`    ${line}`);
            });
            lines.push('');
        }

        // Paramètres output activés
        const enabledParams = outputParams.filter(param => param.enabled);
        if (enabledParams.length > 0) {
            lines.push('    # Configuration des paramètres output');

            enabledParams.forEach(param => {
                if (Array.isArray(param.value)) {
                    // Pour les listes
                    param.value.forEach(item => {
                        if (item.trim()) {
                            lines.push(`    output.${param.parameter}.append(${item})`);
                        }
                    });
                } else {
                    // Pour les valeurs simples
                    if (param.value.trim()) {
                        lines.push(`    output.${param.parameter} = ${param.value}`);
                    }
                }
            });
        }

        return lines.join('\n');
    };

    const handleSave = () => {
        // Convertir vers le format OutputAssignment
        const outputAssignments: OutputAssignment[] = [];

        outputParams.filter(param => param.enabled).forEach(param => {
            if (Array.isArray(param.value)) {
                // Pour les listes
                param.value.forEach((item, index) => {
                    if (item.trim()) {
                        outputAssignments.push({
                            attribute: `${param.parameter}.append`,
                            value: item,
                            lineNumber: 0
                        });
                    }
                });
            } else {
                // Pour les valeurs simples
                if (param.value.trim()) {
                    outputAssignments.push({
                        attribute: param.parameter,
                        value: param.value,
                        lineNumber: 0
                    });
                }
            }
        });

        const updatedRule: RuleConfig = {
            ...rule,
            freeCode: initializationCode,
            outputAssignments,
            code: generateCombinedCode()
        };

        onSave(updatedRule);
    };

    const renderParameterControl = (paramDef: OutputParameterDefinition, paramValue: OutputParameterValue) => {
        const isEnabled = paramValue.enabled;

        if (paramDef.type === 'dropdown') {
            return (
                <select
                    value={isEnabled ? paramValue.value as string : ''}
                    onChange={(e) => handleUpdateParameterValue(paramDef.name, e.target.value)}
                    disabled={!isEnabled}
                    className={`flex-1 border rounded px-2 py-1 text-sm ${!isEnabled ? 'bg-gray-100 text-gray-400' : ''}`}
                >
                    <option value="">-- Sélectionner --</option>
                    {paramDef.options?.map(option => (
                        <option key={option} value={option.startsWith('work_basket_') || option.startsWith('response_template_') ? option : `"${option}"`}>
                            {option.replace(/^(work_basket_|response_template_id_)/, '').replace(/_/g, ' ')}
                        </option>
                    ))}
                </select>
            );
        }

        if (paramDef.type === 'string') {
            return (
                <input
                    type="text"
                    value={isEnabled ? paramValue.value as string : ''}
                    onChange={(e) => handleUpdateParameterValue(paramDef.name, e.target.value)}
                    disabled={!isEnabled}
                    className={`flex-1 border rounded px-2 py-1 text-sm font-mono ${!isEnabled ? 'bg-gray-100 text-gray-400' : ''}`}
                    placeholder={`Valeur pour ${paramDef.name}`}
                />
            );
        }

        if (paramDef.type === 'list') {
            const listValue = paramValue.value as string[];
            return (
                <div className="flex-1">
                    {listValue.map((item, index) => (
                        <div key={index} className="flex gap-2 mb-2">
                            <input
                                type="text"
                                value={item}
                                onChange={(e) => handleUpdateListItem(paramDef.name, index, e.target.value)}
                                disabled={!isEnabled}
                                className={`flex-1 border rounded px-2 py-1 text-sm font-mono ${!isEnabled ? 'bg-gray-100 text-gray-400' : ''}`}
                                placeholder={`Item ${index + 1}`}
                            />
                            {isEnabled && listValue.length > 1 && (
                                <button
                                    onClick={() => handleRemoveListItem(paramDef.name, index)}
                                    className="text-red-500 hover:text-red-700"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            )}
                        </div>
                    ))}
                    {isEnabled && (
                        <button
                            onClick={() => handleAddListItem(paramDef.name)}
                            className="text-blue-500 hover:text-blue-700 text-sm flex items-center gap-1"
                        >
                            <Plus className="w-3 h-3" />
                            Ajouter un item
                        </button>
                    )}
                </div>
            );
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] m-4 flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b">
                    <h2 className="text-xl font-semibold">Édition avancée - {rule.name}</h2>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setShowPreview(!showPreview)}
                            className={`px-3 py-1 rounded text-sm ${showPreview
                                ? 'bg-blue-500 text-white'
                                : 'bg-gray-200 text-gray-700'}`}
                        >
                            {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                        <button onClick={onCancel} className="text-gray-500 hover:text-gray-700">
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex border-b">
                    <button
                        onClick={() => setActiveTab('initialization')}
                        className={`px-4 py-2 font-medium ${activeTab === 'initialization'
                            ? 'border-b-2 border-blue-500 text-blue-600'
                            : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        <Code2 className="w-4 h-4 inline mr-2" />
                        Code d'initialisation
                    </button>
                    <button
                        onClick={() => setActiveTab('output-params')}
                        className={`px-4 py-2 font-medium ${activeTab === 'output-params'
                            ? 'border-b-2 border-blue-500 text-blue-600'
                            : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        <Settings className="w-4 h-4 inline mr-2" />
                        Paramètres output
                    </button>
                </div>

                {/* Content */}
                <div className="flex flex-1 overflow-hidden">
                    <div className={showPreview ? "w-1/2 p-4" : "w-full p-4"}>
                        {activeTab === 'initialization' && (
                            <div className="h-full flex flex-col">
                                <h3 className="text-lg font-medium mb-2">Code d'initialisation</h3>
                                <p className="text-sm text-gray-600 mb-4">
                                    Code pour initialiser des variables, effectuer des calculs, définir des conditions, etc.
                                </p>
                                <textarea
                                    value={initializationCode}
                                    onChange={(e) => setInitializationCode(e.target.value)}
                                    className="flex-1 font-mono text-sm border rounded p-3 resize-none"
                                    placeholder={`if input.intention_id == "${rule.name.replace('rule_', '')}":\n    difference_in_days = jours_jusqu_a_date(input, "date_field")\n    if difference_in_days <= 30:\n        # Logique spécifique`}
                                />
                            </div>
                        )}

                        {activeTab === 'output-params' && (
                            <div className="h-full flex flex-col">
                                <h3 className="text-lg font-medium mb-2">Paramètres output</h3>
                                <p className="text-sm text-gray-600 mb-4">
                                    Configurez tous les paramètres de l'objet CaseHandlingDecisionOutput selon le modèle Pydantic.
                                </p>

                                <div className="space-y-4 flex-1 overflow-y-auto">
                                    {OUTPUT_PARAMETERS.map((paramDef) => {
                                        const paramValue = outputParams.find(p => p.parameter === paramDef.name)!;

                                        return (
                                            <div key={paramDef.name} className="border rounded p-4 bg-gray-50">
                                                <div className="flex items-center gap-3 mb-3">
                                                    <input
                                                        type="checkbox"
                                                        checked={paramValue.enabled}
                                                        onChange={() => handleToggleParameter(paramDef.name)}
                                                        className="w-4 h-4 text-blue-600"
                                                    />
                                                    <div className="flex-1">
                                                        <h4 className="font-medium">{paramDef.name}</h4>
                                                        <p className="text-sm text-gray-600">{paramDef.description}</p>
                                                    </div>
                                                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                                                        {paramDef.type}
                                                    </span>
                                                </div>

                                                <div className="flex gap-2">
                                                    {renderParameterControl(paramDef, paramValue)}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Preview pane */}
                    {showPreview && (
                        <div className="w-1/2 p-4 border-l">
                            <h3 className="text-lg font-medium mb-2">Aperçu du code généré</h3>
                            <pre className="bg-gray-100 p-3 rounded text-sm font-mono h-full overflow-auto whitespace-pre-wrap">
                                {generateCombinedCode()}
                            </pre>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-end gap-2 p-4 border-t">
                    <button
                        onClick={onCancel}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800"
                    >
                        Annuler
                    </button>
                    <button
                        onClick={handleSave}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center gap-2"
                    >
                        <Save className="w-4 h-4" />
                        Enregistrer
                    </button>
                </div>
            </div>
        </div>
    );
}