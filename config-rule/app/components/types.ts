export interface Rule {
  name: string;
  code: string;
  condition?: string | null;
}

export interface Package {
  name: string;
  condition?: string | null;
  execution_order: number;
  rules: Rule[];
}

export interface RuleflowStructure {
  imports: string[];
  constants: string[];
  helper_functions: string[];
  packages: Package[];
  class_name: string;
}



