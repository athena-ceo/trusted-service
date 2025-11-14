import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { RuleflowConfig, ConfigVersion, VersionHistory, ConfigAction, PackageConfig, RuleConfig } from '../types/ruleflow-config';

const LOCKED_PACKAGE_NAME = 'package_initialisations';

const normalizePackageOrder = (packages: PackageConfig[]) => {
    const lockedIndex = packages.findIndex(pkg => pkg.name === LOCKED_PACKAGE_NAME);
    if (lockedIndex > 0) {
        const [lockedPkg] = packages.splice(lockedIndex, 1);
        packages.unshift(lockedPkg);
    }
    packages.forEach((pkg, index) => {
        pkg.execution_order = index;
    });
};

interface RuleflowConfigState {
    // Configuration actuelle
    config: RuleflowConfig | null;

    // Historique des versions pour undo/redo
    history: VersionHistory;

    // État de l'interface
    isModified: boolean;
    isSaving: boolean;
    lastSavedAt: number | null;

    // Actions de configuration
    loadConfig: (appName: string, runtime: string) => Promise<void>;
    saveConfig: (description?: string) => Promise<void>;
    generateCode: () => Promise<void>;

    // Actions d'édition avec versioning automatique
    executeAction: (action: ConfigAction, description?: string) => void;

    // Undo/Redo
    undo: () => boolean;
    redo: () => boolean;
    canUndo: () => boolean;
    canRedo: () => boolean;

    // Gestion de l'historique
    createVersion: (description: string) => void;
    clearHistory: () => void;
    setMaxVersions: (max: number) => void;

    // Utilitaires
    reset: () => void;
    setModified: (modified: boolean) => void;
}

const createInitialConfig = (appName: string, runtime: string): RuleflowConfig => ({
    version: '1.0',
    metadata: {
        app_name: appName,
        class_name: 'DecisionEngine',
        created_at: new Date().toISOString(),
        modified_at: new Date().toISOString(),
        runtime: runtime
    },
    imports: [
        'from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecisionOutput, CaseHandlingDecisionInput'
    ],
    constants: [],
    helper_functions: [],
    packages: [
        {
            id: 'pkg_1',
            name: 'package_initialisations',
            condition: null,
            execution_order: 0,
            rules: [
                {
                    id: 'rule_1',
                    name: 'rule_decision_par_defaut',
                    code: 'output.details.append("rule_decision_par_defaut")\noutput.acknowledgement_to_requester = "#ACK"',
                    condition: null
                }
            ]
        }
    ]
});

const generateId = () => Math.random().toString(36).substr(2, 9);

const cloneConfig = (config: RuleflowConfig): RuleflowConfig => JSON.parse(JSON.stringify(config));

export const useRuleflowConfig = create<RuleflowConfigState>()(
    persist(
        (set, get) => ({
            config: null,
            history: {
                versions: [],
                currentIndex: -1,
                maxVersions: 100
            },
            isModified: false,
            isSaving: false,
            lastSavedAt: null,

            loadConfig: async (appName: string, runtime: string) => {
                try {
                    console.log('🔄 Chargement de la configuration:', { appName, runtime });
                    // Essayer de charger la configuration existante
                    const response = await fetch(`/api/ruleflow/load?app=${encodeURIComponent(appName)}&runtime=${encodeURIComponent(runtime)}`);

                    let config: RuleflowConfig;

                    if (response.ok) {
                        const data = await response.json();
                        config = data.config;
                        console.log('✅ Configuration chargée avec succès, packages:', config.packages.length);
                        console.log('📦 Packages:', config.packages.map(p => ({ name: p.name, rules: p.rules.length })));
                    } else {
                        console.warn('⚠️ Échec du chargement, création d\'une configuration par défaut');
                        // Créer une nouvelle configuration par défaut
                        config = createInitialConfig(appName, runtime);
                    }

                    set({
                        config,
                        isModified: false,
                        history: {
                            versions: [{
                                id: generateId(),
                                timestamp: Date.now(),
                                description: 'Configuration initiale',
                                config: cloneConfig(config)
                            }],
                            currentIndex: 0,
                            maxVersions: 100
                        }
                    });
                } catch (error) {
                    console.error('❌ Erreur lors du chargement de la configuration:', error);
                    // Fallback sur une configuration par défaut
                    const config = createInitialConfig(appName, runtime);
                    set({
                        config,
                        isModified: false,
                        history: {
                            versions: [{
                                id: generateId(),
                                timestamp: Date.now(),
                                description: 'Configuration par défaut',
                                config: cloneConfig(config)
                            }],
                            currentIndex: 0,
                            maxVersions: 100
                        }
                    });
                }
            },

            saveConfig: async (description = 'Sauvegarde automatique') => {
                const { config } = get();
                if (!config) return;

                set({ isSaving: true });

                try {
                    const response = await fetch('/api/ruleflow/save', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            config: {
                                ...config,
                                metadata: {
                                    ...config.metadata,
                                    modified_at: new Date().toISOString()
                                }
                            }
                        })
                    });

                    if (response.ok) {
                        set({
                            isModified: false,
                            lastSavedAt: Date.now(),
                            config: {
                                ...config,
                                metadata: {
                                    ...config.metadata,
                                    modified_at: new Date().toISOString()
                                }
                            }
                        });
                    } else {
                        throw new Error('Erreur lors de la sauvegarde');
                    }
                } catch (error) {
                    console.error('Erreur lors de la sauvegarde:', error);
                    throw error;
                } finally {
                    set({ isSaving: false });
                }
            },

            generateCode: async () => {
                const { config } = get();
                if (!config) return;

                try {
                    const response = await fetch('/api/ruleflow/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ config })
                    });

                    if (!response.ok) {
                        throw new Error('Erreur lors de la génération du code');
                    }

                    const result = await response.json();
                    console.log('Code généré avec succès:', result);
                } catch (error) {
                    console.error('Erreur lors de la génération du code:', error);
                    throw error;
                }
            },

            executeAction: (action: ConfigAction, description?: string) => {
                const { config, history } = get();
                if (!config) return;

                const newConfig = cloneConfig(config);
                newConfig.metadata.modified_at = new Date().toISOString();

                // Exécuter l'action sur la nouvelle configuration
                switch (action.type) {
                    case 'ADD_PACKAGE': {
                        const insertIndex = Math.min(
                            Math.max(action.payload.insertIndex ?? newConfig.packages.length, 0),
                            newConfig.packages.length
                        );
                        const newPackage = {
                            ...action.payload.package,
                            id: generateId(),
                            execution_order: insertIndex
                        };
                        newConfig.packages.splice(insertIndex, 0, newPackage);
                        normalizePackageOrder(newConfig.packages);
                        break;
                    }

                    case 'UPDATE_PACKAGE':
                        const pkgIndex = newConfig.packages.findIndex(p => p.id === action.payload.id);
                        if (pkgIndex >= 0) {
                            newConfig.packages[pkgIndex] = { ...newConfig.packages[pkgIndex], ...action.payload.updates };
                        }
                        break;

                    case 'DELETE_PACKAGE':
                        newConfig.packages = newConfig.packages.filter(p => p.id !== action.payload.id);
                        normalizePackageOrder(newConfig.packages);
                        break;

                    case 'MOVE_PACKAGE':
                        const moveIndex = newConfig.packages.findIndex(p => p.id === action.payload.id);
                        if (moveIndex >= 0) {
                            if (newConfig.packages[moveIndex]?.name === LOCKED_PACKAGE_NAME) {
                                break;
                            }
                            const newIndex = action.payload.direction === 'up' ? moveIndex - 1 : moveIndex + 1;
                            if (newIndex >= 0 && newIndex < newConfig.packages.length) {
                                [newConfig.packages[moveIndex], newConfig.packages[newIndex]] =
                                    [newConfig.packages[newIndex], newConfig.packages[moveIndex]];
                                normalizePackageOrder(newConfig.packages);
                            }
                        }
                        break;
                    case 'REORDER_PACKAGE': {
                        const currentIndex = newConfig.packages.findIndex(p => p.id === action.payload.id);
                        if (currentIndex >= 0) {
                            if (newConfig.packages[currentIndex]?.name === LOCKED_PACKAGE_NAME) {
                                break;
                            }
                            const blockedIndex = newConfig.packages.findIndex(p => p.name === LOCKED_PACKAGE_NAME);
                            const clampedIndex = Math.max(
                                blockedIndex >= 0 ? 1 : 0,
                                Math.min(action.payload.newIndex, newConfig.packages.length - 1)
                            );
                            if (clampedIndex !== currentIndex) {
                                const [pkg] = newConfig.packages.splice(currentIndex, 1);
                                newConfig.packages.splice(clampedIndex, 0, pkg);
                                normalizePackageOrder(newConfig.packages);
                            }
                        }
                        break;
                    }

                    case 'ADD_RULE':
                        const packageForRule = newConfig.packages.find(p => p.id === action.payload.packageId);
                        if (packageForRule) {
                            packageForRule.rules.push({
                                ...action.payload.rule,
                                id: generateId()
                            });
                        }
                        break;

                    case 'UPDATE_RULE':
                        const packageForUpdate = newConfig.packages.find(p => p.id === action.payload.packageId);
                        if (packageForUpdate) {
                            const ruleIndex = packageForUpdate.rules.findIndex(r => r.id === action.payload.ruleId);
                            if (ruleIndex >= 0) {
                                packageForUpdate.rules[ruleIndex] = {
                                    ...packageForUpdate.rules[ruleIndex],
                                    ...action.payload.updates
                                };
                            }
                        }
                        break;

                    case 'DELETE_RULE':
                        const packageForDelete = newConfig.packages.find(p => p.id === action.payload.packageId);
                        if (packageForDelete) {
                            packageForDelete.rules = packageForDelete.rules.filter(r => r.id !== action.payload.ruleId);
                        }
                        break;

                    case 'MOVE_RULE':
                        const packageForMove = newConfig.packages.find(p => p.id === action.payload.packageId);
                        if (packageForMove) {
                            const ruleMoveIndex = packageForMove.rules.findIndex(r => r.id === action.payload.ruleId);
                            if (ruleMoveIndex >= 0) {
                                const newRuleIndex = action.payload.direction === 'up' ? ruleMoveIndex - 1 : ruleMoveIndex + 1;
                                if (newRuleIndex >= 0 && newRuleIndex < packageForMove.rules.length) {
                                    [packageForMove.rules[ruleMoveIndex], packageForMove.rules[newRuleIndex]] =
                                        [packageForMove.rules[newRuleIndex], packageForMove.rules[ruleMoveIndex]];
                                }
                            }
                        }
                        break;

                    case 'UPDATE_RULE_FREE_CODE':
                        const packageForFreeCode = newConfig.packages.find(p => p.id === action.payload.packageId);
                        if (packageForFreeCode) {
                            const ruleIndex = packageForFreeCode.rules.findIndex(r => r.id === action.payload.ruleId);
                            if (ruleIndex >= 0) {
                                packageForFreeCode.rules[ruleIndex] = {
                                    ...packageForFreeCode.rules[ruleIndex],
                                    freeCode: action.payload.freeCode
                                };
                            }
                        }
                        break;

                    case 'UPDATE_OUTPUT_ASSIGNMENT':
                        const packageForOutputUpdate = newConfig.packages.find(p => p.id === action.payload.packageId);
                        if (packageForOutputUpdate) {
                            const ruleIndex = packageForOutputUpdate.rules.findIndex(r => r.id === action.payload.ruleId);
                            if (ruleIndex >= 0) {
                                const rule = packageForOutputUpdate.rules[ruleIndex];
                                if (rule.outputAssignments && action.payload.assignmentIndex < rule.outputAssignments.length) {
                                    rule.outputAssignments[action.payload.assignmentIndex] = action.payload.assignment;
                                }
                            }
                        }
                        break;

                    case 'ADD_OUTPUT_ASSIGNMENT':
                        const packageForOutputAdd = newConfig.packages.find(p => p.id === action.payload.packageId);
                        if (packageForOutputAdd) {
                            const ruleIndex = packageForOutputAdd.rules.findIndex(r => r.id === action.payload.ruleId);
                            if (ruleIndex >= 0) {
                                const rule = packageForOutputAdd.rules[ruleIndex];
                                if (!rule.outputAssignments) {
                                    rule.outputAssignments = [];
                                }
                                rule.outputAssignments.push(action.payload.assignment);
                            }
                        }
                        break;

                    case 'DELETE_OUTPUT_ASSIGNMENT':
                        const packageForOutputDelete = newConfig.packages.find(p => p.id === action.payload.packageId);
                        if (packageForOutputDelete) {
                            const ruleIndex = packageForOutputDelete.rules.findIndex(r => r.id === action.payload.ruleId);
                            if (ruleIndex >= 0) {
                                const rule = packageForOutputDelete.rules[ruleIndex];
                                if (rule.outputAssignments) {
                                    rule.outputAssignments = rule.outputAssignments.filter((_, i) => i !== action.payload.assignmentIndex);
                                }
                            }
                        }
                        break;
                }

                // Créer une nouvelle version dans l'historique
                const newVersion = {
                    id: generateId(),
                    timestamp: Date.now(),
                    description: description || `Action: ${action.type}`,
                    config: cloneConfig(newConfig)
                };

                const newHistory = { ...history };

                // Supprimer les versions après l'index actuel (si on était en mode undo)
                newHistory.versions = newHistory.versions.slice(0, newHistory.currentIndex + 1);

                // Ajouter la nouvelle version
                newHistory.versions.push(newVersion);
                newHistory.currentIndex = newHistory.versions.length - 1;

                // Limiter le nombre de versions
                if (newHistory.versions.length > newHistory.maxVersions) {
                    newHistory.versions = newHistory.versions.slice(-newHistory.maxVersions);
                    newHistory.currentIndex = newHistory.versions.length - 1;
                }

                set({
                    config: newConfig,
                    history: newHistory,
                    isModified: true
                });
            },

            undo: () => {
                const { history } = get();
                if (history.currentIndex > 0) {
                    const newIndex = history.currentIndex - 1;
                    const config = cloneConfig(history.versions[newIndex].config);

                    set({
                        config,
                        history: { ...history, currentIndex: newIndex },
                        isModified: true
                    });
                    return true;
                }
                return false;
            },

            redo: () => {
                const { history } = get();
                if (history.currentIndex < history.versions.length - 1) {
                    const newIndex = history.currentIndex + 1;
                    const config = cloneConfig(history.versions[newIndex].config);

                    set({
                        config,
                        history: { ...history, currentIndex: newIndex },
                        isModified: true
                    });
                    return true;
                }
                return false;
            },

            canUndo: () => {
                const { history } = get();
                return history.currentIndex > 0;
            },

            canRedo: () => {
                const { history } = get();
                return history.currentIndex < history.versions.length - 1;
            },

            createVersion: (description: string) => {
                const { config, history } = get();
                if (!config) return;

                const newVersion = {
                    id: generateId(),
                    timestamp: Date.now(),
                    description,
                    config: cloneConfig(config)
                };

                const newHistory = { ...history };
                newHistory.versions = newHistory.versions.slice(0, newHistory.currentIndex + 1);
                newHistory.versions.push(newVersion);
                newHistory.currentIndex = newHistory.versions.length - 1;

                if (newHistory.versions.length > newHistory.maxVersions) {
                    newHistory.versions = newHistory.versions.slice(-newHistory.maxVersions);
                    newHistory.currentIndex = newHistory.versions.length - 1;
                }

                set({ history: newHistory });
            },

            clearHistory: () => {
                const { config } = get();
                if (!config) return;

                set({
                    history: {
                        versions: [{
                            id: generateId(),
                            timestamp: Date.now(),
                            description: 'Historique vidé',
                            config: cloneConfig(config)
                        }],
                        currentIndex: 0,
                        maxVersions: 100
                    }
                });
            },

            setMaxVersions: (max: number) => {
                const { history } = get();
                const newHistory = { ...history, maxVersions: max };

                if (newHistory.versions.length > max) {
                    newHistory.versions = newHistory.versions.slice(-max);
                    newHistory.currentIndex = Math.min(newHistory.currentIndex, newHistory.versions.length - 1);
                }

                set({ history: newHistory });
            },

            reset: () => {
                set({
                    config: null,
                    history: {
                        versions: [],
                        currentIndex: -1,
                        maxVersions: 100
                    },
                    isModified: false,
                    isSaving: false,
                    lastSavedAt: null
                });
            },

            setModified: (modified: boolean) => {
                set({ isModified: modified });
            }
        }),
        {
            name: 'ruleflow-config-store',
            partialize: (state) => ({
                history: state.history,
                lastSavedAt: state.lastSavedAt
            })
        }
    )
);
