// Types pour le format pivot de configuration de ruleflow

export interface OutputAssignment {
    attribute: string;  // ex: "priority", "work_basket", "acknowledgement_to_requester"
    value: string;     // ex: "HIGH", "work_basket_accueil", "#VISIT_PAGE,text,url"
    lineNumber?: number;
}

export interface RuleConfig {
    id: string;
    name: string;
    code: string;
    freeCode?: string;  // Code libre (logique métier, calculs, conditions)
    outputAssignments?: OutputAssignment[];  // Paramètres output structurés
    condition?: string | null;
}

export interface PackageConfig {
    id: string;
    name: string;
    condition?: string | null;
    execution_order: number;
    rules: RuleConfig[];
}

export interface RuleflowConfig {
    version: string;
    metadata: {
        app_name: string;
        class_name: string;
        created_at: string;
        modified_at: string;
        runtime: string;
    };
    imports: string[];
    constants: string[];
    helper_functions: string[];
    packages: PackageConfig[];
}

export interface ConfigVersion {
    id: string;
    timestamp: number;
    description: string;
    config: RuleflowConfig;
}

export interface VersionHistory {
    versions: ConfigVersion[];
    currentIndex: number;
    maxVersions: number;
}

// Actions pour le système d'undo/redo
export type ConfigAction =
    | { type: 'ADD_PACKAGE'; payload: { package: Omit<PackageConfig, 'id'>; insertIndex?: number } }
    | { type: 'UPDATE_PACKAGE'; payload: { id: string; updates: Partial<PackageConfig> } }
    | { type: 'DELETE_PACKAGE'; payload: { id: string } }
    | { type: 'MOVE_PACKAGE'; payload: { id: string; direction: 'up' | 'down' } }
    | { type: 'REORDER_PACKAGE'; payload: { id: string; newIndex: number } }
    | { type: 'ADD_RULE'; payload: { packageId: string; rule: Omit<RuleConfig, 'id'> } }
    | { type: 'UPDATE_RULE'; payload: { packageId: string; ruleId: string; updates: Partial<RuleConfig> } }
    | { type: 'DELETE_RULE'; payload: { packageId: string; ruleId: string } }
    | { type: 'MOVE_RULE'; payload: { packageId: string; ruleId: string; direction: 'up' | 'down' } }
    | { type: 'UPDATE_RULE_FREE_CODE'; payload: { packageId: string; ruleId: string; freeCode: string } }
    | { type: 'UPDATE_OUTPUT_ASSIGNMENT'; payload: { packageId: string; ruleId: string; assignmentIndex: number; assignment: OutputAssignment } }
    | { type: 'ADD_OUTPUT_ASSIGNMENT'; payload: { packageId: string; ruleId: string; assignment: OutputAssignment } }
    | { type: 'DELETE_OUTPUT_ASSIGNMENT'; payload: { packageId: string; ruleId: string; assignmentIndex: number } };
