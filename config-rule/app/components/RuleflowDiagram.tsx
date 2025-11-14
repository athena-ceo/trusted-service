'use client';

import { useMemo } from 'react';
import { Package } from './types';

// Fonction pour formater le nom du package pour affichage
const formatPackageName = (name: string): string => {
    // Enlever le préfixe "package_" s'il existe
    let formatted = name.startsWith('package_') ? name.substring(8) : name;
    // Remplacer les "_" par des espaces
    formatted = formatted.replace(/_/g, ' ');
    // Capitaliser le premier mot
    if (formatted.length > 0) {
        formatted = formatted.charAt(0).toUpperCase() + formatted.slice(1);
    }
    return formatted;
};

interface RuleflowDiagramProps {
    packages: Package[];
    selectedPackage?: string;
    onSelectPackage?: (packageName: string) => void;
}

export default function RuleflowDiagram({ packages, selectedPackage, onSelectPackage }: RuleflowDiagramProps) {
    const diagramData = useMemo(() => {
        // Trier les packages par ordre d'exécution
        const sortedPackages = [...packages].sort((a, b) => a.execution_order - b.execution_order);

        // Calculer les positions des packages
        const packagePositions = sortedPackages.map((pkg, index) => ({
            ...pkg,
            x: 50,
            y: 80 + index * 120,
            width: 180,
            height: 80
        }));

        return packagePositions;
    }, [packages]);

    const handlePackageClick = (packageName: string) => {
        onSelectPackage?.(packageName);
    };

    return (
        <div className="h-full overflow-auto">
            <svg
                width="280"
                height={Math.max(400, packages.length * 120 + 160)}
                className="w-full"
            >
                {/* Titre */}
                <text x="140" y="30" textAnchor="middle" className="text-lg font-semibold fill-gray-700">
                    Ruleflow Execution
                </text>

                {/* Flèche de flux principal */}
                {diagramData.length > 1 && (
                    <g>
                        <defs>
                            <marker id="arrowhead" markerWidth="10" markerHeight="7"
                                refX="9" refY="3.5" orient="auto">
                                <polygon points="0 0, 10 3.5, 0 7" fill="#6B7280" />
                            </marker>
                        </defs>

                        {diagramData.slice(0, -1).map((pkg, index) => (
                            <line
                                key={`arrow-${index}`}
                                x1="140"
                                y1={pkg.y + pkg.height}
                                x2="140"
                                y2={diagramData[index + 1].y}
                                stroke="#6B7280"
                                strokeWidth="2"
                                markerEnd="url(#arrowhead)"
                            />
                        ))}
                    </g>
                )}

                {/* Packages */}
                {diagramData.map((pkg, index) => (
                    <g key={pkg.name}>
                        {/* Rectangle du package */}
                        <rect
                            x={pkg.x}
                            y={pkg.y}
                            width={pkg.width}
                            height={pkg.height}
                            rx="8"
                            fill={selectedPackage === pkg.name ? "#EFF6FF" : "#F9FAFB"}
                            stroke={selectedPackage === pkg.name ? "#2563EB" : "#E5E7EB"}
                            strokeWidth={selectedPackage === pkg.name ? "2" : "1"}
                            className="cursor-pointer hover:fill-blue-50 hover:stroke-blue-300 transition-colors"
                            onClick={() => handlePackageClick(pkg.name)}
                        />

                        {/* Nom du package */}
                        <text
                            x={pkg.x + pkg.width / 2}
                            y={pkg.y + 25}
                            textAnchor="middle"
                            className="text-sm font-medium fill-gray-900 pointer-events-none"
                        >
                            {formatPackageName(pkg.name)}
                        </text>

                        {/* Ordre d'exécution */}
                        <text
                            x={pkg.x + pkg.width / 2}
                            y={pkg.y + 45}
                            textAnchor="middle"
                            className="text-xs fill-gray-500 pointer-events-none"
                        >
                            Order: {pkg.execution_order}
                        </text>

                        {/* Nombre de règles */}
                        <text
                            x={pkg.x + pkg.width / 2}
                            y={pkg.y + 65}
                            textAnchor="middle"
                            className="text-xs fill-gray-600 pointer-events-none"
                        >
                            {pkg.rules.length} rule{pkg.rules.length !== 1 ? 's' : ''}
                        </text>

                        {/* Condition si présente */}
                        {pkg.condition && (
                            <text
                                x={pkg.x + pkg.width / 2}
                                y={pkg.y - 10}
                                textAnchor="middle"
                                className="text-xs fill-orange-600 pointer-events-none"
                            >
                                ⚠ Conditional
                            </text>
                        )}

                        {/* Indicateur de sélection */}
                        {selectedPackage === pkg.name && (
                            <circle
                                cx={pkg.x + pkg.width - 15}
                                cy={pkg.y + 15}
                                r="6"
                                fill="#2563EB"
                                className="pointer-events-none"
                            />
                        )}
                    </g>
                ))}

                {/* Légende */}
                <g transform="translate(20, 50)">
                    <text x="0" y="0" className="text-xs fill-gray-500">
                        Click packages to edit
                    </text>
                </g>
            </svg>
        </div>
    );
}