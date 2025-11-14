'use client';

import { useState } from 'react';
import { Code2, Settings, Eye, EyeOff, Save, X } from 'lucide-react';
import { RuleConfig, OutputAssignment } from '../types/ruleflow-config';

interface AdvancedRuleEditorProps {
    rule: RuleConfig;
    onSave: (updatedRule: RuleConfig) => void;
    onCancel: () => void;
}

export default function AdvancedRuleEditor({ rule, onSave, onCancel }: AdvancedRuleEditorProps) {
    const [activeTab, setActiveTab] = useState<'free-code' | 'output-params'>('free-code');
    const [freeCode, setFreeCode] = useState(rule.freeCode || '');
    const [outputAssignments, setOutputAssignments] = useState<OutputAssignment[]>(
        rule.outputAssignments || []
    );
    const [showPreview, setShowPreview] = useState(false);

    const handleAddOutputAssignment = () => {
        const newAssignment: OutputAssignment = {
            attribute: 'priority',
            value: 'MEDIUM',
            lineNumber: 0
        };
        setOutputAssignments([...outputAssignments, newAssignment]);
    };

    const handleUpdateOutputAssignment = (index: number, assignment: OutputAssignment) => {
        const updated = [...outputAssignments];
        updated[index] = assignment;
        setOutputAssignments(updated);
    };

    const handleDeleteOutputAssignment = (index: number) => {
        const updated = outputAssignments.filter((_, i) => i !== index);
        setOutputAssignments(updated);
    };

    const generateCombinedCode = () => {
        // Génération du code combiné pour l'aperçu
        const lines = [];
        lines.push(`def ${rule.name}(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):`);

        if (freeCode.trim()) {
            const freeCodeLines = freeCode.split('\n');
            freeCodeLines.forEach(line => {
                lines.push(`    ${line}`);
            });
        }

        if (outputAssignments.length > 0) {
            lines.push('    # Mise à jour des paramètres output');
            outputAssignments.forEach(assignment => {
                if (assignment.attribute.includes('.append')) {
                    const [listName] = assignment.attribute.split('.append');
                    lines.push(`    output.${listName}.append(${assignment.value})`);
                } else {
                    lines.push(`    output.${assignment.attribute} = ${assignment.value}`);
                }
            });
        }

        return lines.join('\n');
    };

    const handleSave = () => {
        const updatedRule: RuleConfig = {
            ...rule,
            freeCode,
            outputAssignments,
            code: generateCombinedCode() // Mettre à jour le code complet
        };
        onSave(updatedRule);
    };

    const availableOutputAttributes = [
        'priority',
        'handling',
        'work_basket',
        'acknowledgement_to_requester',
        'response_template_id',
        'details.append',
        'notes.append'
    ];

    const priorityValues = ['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'];
    const handlingValues = ['AUTOMATED', 'AGENT', 'DEFLECTION'];

    // Extraire les workbaskets et templates depuis les constantes (simulé pour le moment)
    const workBasketValues = [
        'work_basket_accueil',
        'work_basket_pref_etrangers_aes_salarie',
        'work_basket_api_a_renouveler',
        'work_basket_asile_priorite',
        'work_basket_atda',
        'work_basket_generique',
        'work_basket_dublin',
        'work_basket_reorientation',
        'work_basket_sauf_conduits',
        'work_basket_ukraine'
    ];

    const responseTemplateValues = [
        'response_template_id_api_a_renouveler',
        'response_template_id_atda',
        'response_template_id_dublin',
        'response_template_id_sauf_conduits'
    ];

    const getValueOptions = (attribute: string) => {
        switch (attribute) {
            case 'priority':
                return priorityValues.map(val => ({ value: `"${val}"`, label: val }));
            case 'handling':
                return handlingValues.map(val => ({ value: `"${val}"`, label: val }));
            case 'work_basket':
                return workBasketValues.map(val => ({ value: val, label: val.replace('work_basket_', '').replace('_', ' ') }));
            case 'response_template_id':
                return responseTemplateValues.map(val => ({ value: val, label: val.replace('response_template_id_', '').replace('_', ' ') }));
            default:
                return [];
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
                                ? 'bg-blue-100 text-blue-700'
                                : 'bg-gray-100 text-gray-700'
                                }`}
                        >
                            {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            {showPreview ? 'Masquer aperçu' : 'Aperçu'}
                        </button>
                        <button onClick={onCancel} className="p-1 hover:bg-gray-100 rounded">
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex border-b">
                    <button
                        onClick={() => setActiveTab('free-code')}
                        className={`px-4 py-2 flex items-center gap-2 ${activeTab === 'free-code'
                            ? 'border-b-2 border-blue-500 text-blue-600'
                            : 'text-gray-600'
                            }`}
                    >
                        <Code2 className="w-4 h-4" />
                        Code libre
                    </button>
                    <button
                        onClick={() => setActiveTab('output-params')}
                        className={`px-4 py-2 flex items-center gap-2 ${activeTab === 'output-params'
                            ? 'border-b-2 border-blue-500 text-blue-600'
                            : 'text-gray-600'
                            }`}
                    >
                        <Settings className="w-4 h-4" />
                        Paramètres output
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 flex">
                    {/* Editor pane */}
                    <div className={`${showPreview ? 'w-1/2' : 'w-full'} p-4 border-r`}>
                        {activeTab === 'free-code' && (
                            <div className="h-full flex flex-col">
                                <h3 className="text-lg font-medium mb-2">Code libre</h3>
                                <p className="text-sm text-gray-600 mb-4">
                                    Saisissez votre logique métier, conditions, calculs, etc.
                                </p>
                                <textarea
                                    value={freeCode}
                                    onChange={(e) => setFreeCode(e.target.value)}
                                    className="flex-1 font-mono text-sm border rounded p-3 resize-none"
                                    placeholder="if input.intention_id == 'example':&#10;    difference_in_days = jours_jusqu_a_date(input, 'date_field')&#10;    if difference_in_days <= 30:&#10;        # Logique spécifique"
                                />
                            </div>
                        )}

                        {activeTab === 'output-params' && (
                            <div className="h-full flex flex-col">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-lg font-medium">Paramètres output</h3>
                                    <button
                                        onClick={handleAddOutputAssignment}
                                        className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
                                    >
                                        + Ajouter
                                    </button>
                                </div>
                                <p className="text-sm text-gray-600 mb-4">
                                    Configurez les paramètres de l'objet CaseHandlingDecisionOutput.
                                </p>

                                <div className="space-y-3 flex-1 overflow-y-auto">
                                    {outputAssignments.map((assignment, index) => (
                                        <div key={index} className="border rounded p-3 bg-gray-50">
                                            <div className="flex items-center gap-2 mb-2">
                                                <select
                                                    value={assignment.attribute}
                                                    onChange={(e) => handleUpdateOutputAssignment(index, {
                                                        ...assignment,
                                                        attribute: e.target.value
                                                    })}
                                                    className="flex-1 border rounded px-2 py-1 text-sm"
                                                >
                                                    {availableOutputAttributes.map(attr => (
                                                        <option key={attr} value={attr}>{attr}</option>
                                                    ))}
                                                </select>
                                                <button
                                                    onClick={() => handleDeleteOutputAssignment(index)}
                                                    className="text-red-500 hover:text-red-700"
                                                >
                                                    <X className="w-4 h-4" />
                                                </button>
                                            </div>

                                            <div className="flex gap-2">
                                                {(() => {
                                                    const options = getValueOptions(assignment.attribute);
                                                    if (options.length > 0) {
                                                        return (
                                                            <select
                                                                value={assignment.value}
                                                                onChange={(e) => handleUpdateOutputAssignment(index, {
                                                                    ...assignment,
                                                                    value: e.target.value
                                                                })}
                                                                className="flex-1 border rounded px-2 py-1 text-sm"
                                                            >
                                                                {options.map(option => (
                                                                    <option key={option.value} value={option.value}>
                                                                        {option.label}
                                                                    </option>
                                                                ))}
                                                            </select>
                                                        );
                                                    } else {
                                                        return (
                                                            <input
                                                                type="text"
                                                                value={assignment.value}
                                                                onChange={(e) => handleUpdateOutputAssignment(index, {
                                                                    ...assignment,
                                                                    value: e.target.value
                                                                })}
                                                                className="flex-1 border rounded px-2 py-1 text-sm font-mono"
                                                                placeholder={assignment.attribute.includes('append')
                                                                    ? `"valeur à ajouter"`
                                                                    : "Valeur ou expression Python"}
                                                            />
                                                        );
                                                    }
                                                })()}
                                            </div>
                                        </div>
                                    ))}

                                    {outputAssignments.length === 0 && (
                                        <div className="text-center text-gray-500 py-8">
                                            Aucun paramètre output configuré.
                                            <br />
                                            Cliquez sur "Ajouter" pour commencer.
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Preview pane */}
                    {showPreview && (
                        <div className="w-1/2 p-4">
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