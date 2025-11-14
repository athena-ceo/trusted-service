'use client';

import { useRuleflowConfig } from '../stores/ruleflow-config-store';
import { useState } from 'react';

export default function ConfigToolbar() {
    const {
        config,
        isModified,
        isSaving,
        lastSavedAt,
        undo,
        redo,
        canUndo,
        canRedo,
        saveConfig,
        generateCode,
        clearHistory,
        history
    } = useRuleflowConfig();

    const [isGenerating, setIsGenerating] = useState(false);
    const [showHistory, setShowHistory] = useState(false);

    const handleSave = async () => {
        try {
            await saveConfig('Sauvegarde manuelle');
        } catch (error) {
            console.error('Erreur lors de la sauvegarde:', error);
            // TODO: Afficher une notification d'erreur
        }
    };

    const handleGenerate = async () => {
        try {
            setIsGenerating(true);
            await generateCode();
            // TODO: Afficher une notification de succès
        } catch (error) {
            console.error('Erreur lors de la génération:', error);
            // TODO: Afficher une notification d'erreur
        } finally {
            setIsGenerating(false);
        }
    };

    const handleUndo = () => {
        undo();
    };

    const handleRedo = () => {
        redo();
    };

    const formatTimestamp = (timestamp: number) => {
        return new Date(timestamp).toLocaleString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    const currentVersion = history.versions[history.currentIndex];

    if (!config) {
        return null;
    }

    return (
        <div className="bg-white border-b border-gray-200 px-4 py-3 shadow-sm">
            <div className="flex items-center justify-between">
                {/* Informations de configuration */}
                <div className="flex items-center space-x-4">
                    <div className="text-sm">
                        <span className="font-medium text-gray-900">
                            {config.metadata.app_name}
                        </span>
                        <span className="text-gray-500 ml-2">
                            ({config.metadata.runtime})
                        </span>
                    </div>

                    {isModified && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            Non sauvegardé
                        </span>
                    )}

                    {lastSavedAt && (
                        <span className="text-xs text-gray-500">
                            Dernier save: {formatTimestamp(lastSavedAt)}
                        </span>
                    )}
                </div>

                {/* Actions principales */}
                <div className="flex items-center space-x-2">
                    {/* Undo/Redo */}
                    <div className="flex items-center border border-gray-300 rounded-md">
                        <button
                            onClick={handleUndo}
                            disabled={!canUndo()}
                            className="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed border-r border-gray-300"
                            title="Annuler (Ctrl+Z)"
                        >
                            ↶
                        </button>
                        <button
                            onClick={handleRedo}
                            disabled={!canRedo()}
                            className="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
                            title="Rétablir (Ctrl+Y)"
                        >
                            ↷
                        </button>
                    </div>

                    {/* Historique */}
                    <div className="relative">
                        <button
                            onClick={() => setShowHistory(!showHistory)}
                            className="px-3 py-1.5 text-sm font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                            title={`Historique (${history.versions.length} versions)`}
                        >
                            📜 {history.currentIndex + 1}/{history.versions.length}
                        </button>

                        {showHistory && (
                            <div className="absolute right-0 mt-1 w-80 bg-white border border-gray-300 rounded-md shadow-lg z-10 max-h-60 overflow-y-auto">
                                <div className="px-3 py-2 border-b border-gray-200 font-medium text-gray-900">
                                    Historique des versions
                                </div>
                                {history.versions.map((version, index) => (
                                    <div
                                        key={version.id}
                                        className={`px-3 py-2 text-sm border-b border-gray-100 last:border-b-0 ${index === history.currentIndex
                                                ? 'bg-blue-50 border-l-4 border-l-blue-500'
                                                : 'hover:bg-gray-50'
                                            }`}
                                    >
                                        <div className="font-medium text-gray-900">
                                            {version.description}
                                        </div>
                                        <div className="text-xs text-gray-500 mt-1">
                                            {formatTimestamp(version.timestamp)}
                                        </div>
                                    </div>
                                ))}
                                <div className="px-3 py-2 border-t border-gray-200">
                                    <button
                                        onClick={() => {
                                            clearHistory();
                                            setShowHistory(false);
                                        }}
                                        className="text-xs text-red-600 hover:text-red-800"
                                    >
                                        Vider l'historique
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Sauvegarde */}
                    <button
                        onClick={handleSave}
                        disabled={isSaving || !isModified}
                        className="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-md"
                    >
                        {isSaving ? 'Sauvegarde...' : 'Sauvegarder'}
                    </button>

                    {/* Génération de code */}
                    <button
                        onClick={handleGenerate}
                        disabled={isGenerating}
                        className="px-4 py-1.5 text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-md"
                    >
                        {isGenerating ? 'Génération...' : 'Générer le code'}
                    </button>
                </div>
            </div>
        </div>
    );
}