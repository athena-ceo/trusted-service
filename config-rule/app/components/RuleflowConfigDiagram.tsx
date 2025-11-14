'use client';

import { useMemo, useState, useRef, useCallback, useEffect } from 'react';
import { PackageConfig } from '../types/ruleflow-config';

const LOCKED_PACKAGE_NAME = 'package_initialisations';

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
    packages: PackageConfig[];
    selectedPackage?: string | null;
    onSelectPackage?: (packageId: string) => void;
    onReorderPackage?: (packageId: string, newIndex: number) => void;
}

export default function RuleflowDiagram({ packages, selectedPackage, onSelectPackage, onReorderPackage }: RuleflowDiagramProps) {
    // Position du bloc de légende (déplaçable)
    const [legendPosition, setLegendPosition] = useState({ x: 10, y: 10 });
    const [isLegendDragging, setIsLegendDragging] = useState(false);
    const [legendDragOffset, setLegendDragOffset] = useState({ x: 0, y: 0 });
    const [showLegend, setShowLegend] = useState(true);
    const legendRef = useRef<SVGGElement>(null);
    const svgRef = useRef<SVGSVGElement>(null);
    const suppressClickRef = useRef(false);

    const [animatedPositions, setAnimatedPositions] = useState<Record<string, number>>({});
    const animatedPositionsRef = useRef<Record<string, number>>({});
    const animationTargetsRef = useRef<Record<string, { from: number; to: number }>>({});
    const animationFrameRef = useRef<number | null>(null);
    const animationStartRef = useRef<number>(0);

    const [draggingPackage, setDraggingPackage] = useState<{
        id: string;
        offsetY: number;
        currentY: number;
        originalIndex: number;
        hasMoved: boolean;
    } | null>(null);
    const [dragInsertIndex, setDragInsertIndex] = useState<number | null>(null);

    // Dimensions du diagramme - vérifier la largeur réelle du conteneur
    const svgWidth = 400; // Largeur augmentée pour accommoder la colonne agrandie
    const centerX = svgWidth / 2;
    const packageWidth = 200;
    const packageHeight = 80;
    const startY = 140; // Décalage initial pour laisser de la place au START
    const svgHeight = Math.max(400, packages.length * 120 + 300);

    const diagramData = useMemo(() => {
        // Trier les packages par ordre d'exécution
        const sortedPackages = [...packages].sort((a, b) => a.execution_order - b.execution_order);

        const packageX = centerX - packageWidth / 2; // Centrer le package

        // Calculer les positions des packages (décalés vers le bas pour laisser de la place à la légende et au START)
        const packagePositions = sortedPackages.map((pkg, index) => ({
            ...pkg,
            x: packageX,
            y: startY + index * 120,
            width: packageWidth,
            height: packageHeight,
            centerX: centerX
        }));

        return packagePositions;
    }, [packages, centerX, packageWidth, packageHeight, startY]);

    useEffect(() => {
        animatedPositionsRef.current = animatedPositions;
    }, [animatedPositions]);

    const startAnimation = useCallback(() => {
        if (animationFrameRef.current !== null) {
            cancelAnimationFrame(animationFrameRef.current);
            animationFrameRef.current = null;
        }

        const animate = (time: number) => {
            const progress = Math.min(1, (time - animationStartRef.current) / 1000);
            const nextPositions: Record<string, number> = { ...animatedPositionsRef.current };

            Object.entries(animationTargetsRef.current).forEach(([id, target]) => {
                nextPositions[id] = target.from + (target.to - target.from) * progress;
            });

            animatedPositionsRef.current = nextPositions;
            setAnimatedPositions(nextPositions);

            if (progress < 1) {
                animationFrameRef.current = requestAnimationFrame(animate);
            } else {
                animationFrameRef.current = null;
            }
        };

        animationFrameRef.current = requestAnimationFrame(animate);
    }, []);

    useEffect(() => {
        const currentPositions = { ...animatedPositionsRef.current };
        let updated = false;
        const currentIds = new Set(diagramData.map(pkg => pkg.id));

        Object.keys(currentPositions).forEach(id => {
            if (!currentIds.has(id)) {
                delete currentPositions[id];
                updated = true;
            }
        });

        diagramData.forEach(pkg => {
            if (currentPositions[pkg.id] === undefined) {
                currentPositions[pkg.id] = pkg.y;
                updated = true;
            }
        });

        if (updated) {
            animatedPositionsRef.current = currentPositions;
            setAnimatedPositions(currentPositions);
        }

        const targets: Record<string, { from: number; to: number }> = {};
        diagramData.forEach(pkg => {
            const current = animatedPositionsRef.current[pkg.id];
            if (current === undefined) {
                targets[pkg.id] = { from: pkg.y, to: pkg.y };
            } else if (Math.abs(current - pkg.y) > 0.5) {
                targets[pkg.id] = { from: current, to: pkg.y };
            }
        });

        const hasMovement = Object.values(targets).some(target => Math.abs(target.from - target.to) > 0.5);
        if (!hasMovement) {
            return;
        }

        animationTargetsRef.current = targets;
        animationStartRef.current = performance.now();
        startAnimation();
    }, [diagramData, startAnimation]);

    useEffect(() => {
        return () => {
            if (animationFrameRef.current !== null) {
                cancelAnimationFrame(animationFrameRef.current);
            }
        };
    }, []);

    const handlePackageClick = (packageId: string) => {
        if (suppressClickRef.current) {
            suppressClickRef.current = false;
            return;
        }
        onSelectPackage?.(packageId);
    };

    const getSvgPoint = useCallback((event: React.MouseEvent<Element>) => {
        const svg = svgRef.current;
        if (!svg) return null;
        const point = svg.createSVGPoint();
        point.x = event.clientX;
        point.y = event.clientY;
        const matrix = svg.getScreenCTM();
        if (!matrix) return null;
        return point.matrixTransform(matrix.inverse());
    }, []);

    const computeInsertIndex = useCallback((draggedId: string, proposedY: number) => {
        const dragCenter = proposedY + packageHeight / 2;
        const otherPackages = diagramData.filter(pkg => pkg.id !== draggedId);
        const hasLockedPackage = otherPackages.some(p => p.name === LOCKED_PACKAGE_NAME);
        const minIndex = hasLockedPackage ? 1 : 0;
        for (let i = 0; i < otherPackages.length; i++) {
            const pkg = otherPackages[i];
            const pkgCenter = pkg.y + packageHeight / 2;
            if (dragCenter < pkgCenter) {
                return Math.max(minIndex, i);
            }
        }
        return Math.max(minIndex, otherPackages.length);
    }, [diagramData, packageHeight]);

    // Gestion du drag and drop pour la légende
    const handleLegendMouseDown = useCallback((e: React.MouseEvent<SVGGElement>) => {
        e.stopPropagation();
        const svgPoint = getSvgPoint(e);
        if (!svgPoint) return;
        setIsLegendDragging(true);
        setLegendDragOffset({
            x: svgPoint.x - legendPosition.x,
            y: svgPoint.y - legendPosition.y
        });
    }, [getSvgPoint, legendPosition]);

    const handleMouseMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
        const svgPoint = getSvgPoint(e);
        if (!svgPoint) return;

        if (isLegendDragging) {
            const newX = svgPoint.x - legendDragOffset.x;
            const newY = svgPoint.y - legendDragOffset.y;

            // Limiter la position dans les limites du SVG
            const maxX = svgWidth - 200; // largeur SVG - largeur légende
            const maxY = svgHeight - 25; // hauteur SVG - hauteur légende

            setLegendPosition({
                x: Math.max(0, Math.min(newX, maxX)),
                y: Math.max(0, Math.min(newY, maxY))
            });
        }

        if (draggingPackage) {
            const proposedY = svgPoint.y - draggingPackage.offsetY;
            const minY = startY - packageHeight;
            const maxY = svgHeight - packageHeight - 40;
            const clampedY = Math.max(minY, Math.min(proposedY, maxY));
            const hasMoved = draggingPackage.hasMoved || Math.abs(clampedY - draggingPackage.currentY) > 2;

            if (hasMoved) {
                suppressClickRef.current = true;
            }

            setDraggingPackage(prev => prev ? {
                ...prev,
                currentY: clampedY,
                hasMoved
            } : prev);

            const newIndex = computeInsertIndex(draggingPackage.id, clampedY);
            setDragInsertIndex(newIndex);
        }
    }, [computeInsertIndex, draggingPackage, getSvgPoint, isLegendDragging, legendDragOffset, svgHeight, svgWidth, startY, packageHeight]);

    const handleMouseUp = useCallback(() => {
        if (isLegendDragging) {
            setIsLegendDragging(false);
        }

        if (draggingPackage) {
            const { id, originalIndex, hasMoved } = draggingPackage;
            setAnimatedPositions(prev => {
                const next = { ...prev, [id]: draggingPackage.currentY };
                animatedPositionsRef.current = next;
                return next;
            });
            if (hasMoved && dragInsertIndex !== null) {
                const clampedIndex = Math.max(0, Math.min(dragInsertIndex, packages.length - 1));
                if (clampedIndex !== originalIndex) {
                    onReorderPackage?.(id, clampedIndex);
                }
            }
            suppressClickRef.current = hasMoved;
            setDraggingPackage(null);
            setDragInsertIndex(null);
        }
    }, [dragInsertIndex, draggingPackage, isLegendDragging, onReorderPackage, packages.length]);

    const handlePackageMouseDown = (pkgId: string, index: number, initialY: number, isLocked: boolean) => (e: React.MouseEvent<SVGElement>) => {
        if (!onReorderPackage || isLocked) return;
        if (e.button !== 0) return;
        e.stopPropagation();
        const svgPoint = getSvgPoint(e);
        if (!svgPoint) return;
        suppressClickRef.current = false;
        setDraggingPackage({
            id: pkgId,
            offsetY: svgPoint.y - initialY,
            currentY: initialY,
            originalIndex: index,
            hasMoved: false
        });
        setDragInsertIndex(index);
    };

    const resolvePackageY = useCallback((pkgId: string, defaultY: number) => {
        if (draggingPackage?.id === pkgId) {
            return draggingPackage.currentY;
        }
        return animatedPositions[pkgId] ?? defaultY;
    }, [draggingPackage, animatedPositions]);

    const firstPackage = diagramData[0];
    const firstPackageY = firstPackage ? resolvePackageY(firstPackage.id, firstPackage.y) : null;
    const lastPackage = diagramData[diagramData.length - 1];
    const lastPackageY = lastPackage ? resolvePackageY(lastPackage.id, lastPackage.y) : null;
    const endBaseY = (lastPackageY ?? 128) + packageHeight;

    if (packages.length === 0) {
        return (
            <div className="flex items-center justify-center h-48 bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg">
                <div className="text-center">
                    <div className="text-4xl mb-2">📋</div>
                    <p className="text-gray-500">Aucun package à afficher</p>
                </div>
            </div>
        );
    }

    return (
        <div className="h-full overflow-auto bg-gray-50 rounded-lg border">
            <svg
                ref={svgRef}
                width={svgWidth}
                height={svgHeight}
                className="w-full"
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
            >
                <defs>
                    <marker
                        id="arrowhead"
                        markerWidth="10"
                        markerHeight="7"
                        refX="9"
                        refY="3.5"
                        orient="auto"
                        fill="#6b7280"
                    >
                        <polygon points="0 0, 10 3.5, 0 7" />
                    </marker>

                    <filter id="drop-shadow">
                        <feDropShadow dx="2" dy="4" stdDeviation="3" floodOpacity="0.1" />
                    </filter>
                </defs>

                {/* Ligne pointillée entre START et premier package */}
                {diagramData.length > 0 && firstPackageY !== null && (
                    <line
                        x1={centerX}
                        y1={92}
                        x2={centerX}
                        y2={firstPackageY - 20}
                        stroke="#d1d5db"
                        strokeWidth="2"
                        strokeDasharray="5,5"
                    />
                )}
                {/* Flèche simple depuis START vers premier package */}
                {diagramData.length > 0 && firstPackageY !== null && (
                    <line
                        x1={centerX}
                        y1={firstPackageY - 20}
                        x2={centerX}
                        y2={firstPackageY}
                        stroke="#6b7280"
                        strokeWidth="2"
                        markerEnd="url(#arrowhead)"
                    />
                )}

                {/* Point de départ */}
                <g>
                    <circle
                        cx={centerX}
                        cy={80}
                        r="12"
                        fill="#10b981"
                        filter="url(#drop-shadow)"
                    />
                    <text
                        x={centerX}
                        y={85}
                        textAnchor="middle"
                        className="fill-white text-xs font-bold"
                    >
                        ▶
                    </text>
                    <text
                        x={centerX}
                        y={65}
                        textAnchor="middle"
                        className="fill-gray-600 text-xs font-medium"
                    >
                        START
                    </text>
                </g>

                {/* Packages */}
                {diagramData.map((pkg, index) => {
                    const isLocked = pkg.name === LOCKED_PACKAGE_NAME;
                    const isSelected = selectedPackage === pkg.id;
                    const isConditional = pkg.condition !== null && pkg.condition !== '';
                    const previousPackage = index > 0 ? diagramData[index - 1] : null;
                    const currentY = resolvePackageY(pkg.id, pkg.y);
                    const previousY = previousPackage ? resolvePackageY(previousPackage.id, previousPackage.y) : null;
                    const isDraggable = Boolean(onReorderPackage);

                    return (
                        <g
                            key={pkg.id}
                            className={isDraggable && !isLocked ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer'}
                            onMouseDown={isDraggable && !isLocked ? handlePackageMouseDown(pkg.id, index, currentY, isLocked) : undefined}
                        >
                            {/* Flèche simple entre packages (une seule flèche par espace) */}
                            {previousPackage && previousY !== null && (
                                <line
                                    x1={pkg.centerX}
                                    y1={previousY + packageHeight}
                                    x2={pkg.centerX}
                                    y2={currentY}
                                    stroke="#6b7280"
                                    strokeWidth="2"
                                    markerEnd="url(#arrowhead)"
                                />
                            )}

                            {/* Rectangle principal du package */}
                            <rect
                                x={pkg.x}
                                y={currentY}
                                width={pkg.width}
                                height={pkg.height}
                                rx="8"
                                fill={isSelected ? "#dbeafe" : "#ffffff"}
                                stroke={isSelected ? "#3b82f6" : isConditional ? "#f59e0b" : "#d1d5db"}
                                strokeWidth={isSelected ? "3" : "2"}
                                className={`${isDraggable && !isLocked ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer'} hover:stroke-blue-400 transition-colors`}
                                filter="url(#drop-shadow)"
                                onClick={() => handlePackageClick(pkg.id)}
                            />

                            {/* Indicateur de condition */}
                            {isConditional && (
                                <g>
                                    <polygon
                                        points={`${pkg.x + pkg.width - 20},${currentY} ${pkg.x + pkg.width},${currentY} ${pkg.x + pkg.width},${currentY + 20}`}
                                        fill="#f59e0b"
                                    />
                                    <text
                                        x={pkg.x + pkg.width - 10}
                                        y={currentY + 14}
                                        textAnchor="middle"
                                        className="fill-white text-xs font-bold"
                                    >
                                        ?
                                    </text>
                                </g>
                            )}

                            {/* Numéro d'ordre */}
                            <circle
                                cx={pkg.x + 15}
                                cy={currentY + 15}
                                r="10"
                                fill={isSelected ? "#3b82f6" : "#6b7280"}
                            />
                            <text
                                x={pkg.x + 15}
                                y={currentY + 20}
                                textAnchor="middle"
                                className="fill-white text-xs font-bold"
                            >
                                {index + 1}
                            </text>

                            {/* Nom du package */}
                            <text
                                x={pkg.x + 35}
                                y={currentY + 20}
                                className={`text-sm font-medium ${isSelected ? "fill-blue-900" : "fill-gray-900"}`}
                            >
                                {formatPackageName(pkg.name)}
                            </text>

                            {/* Nombre de règles */}
                            <text
                                x={pkg.x + 35}
                                y={currentY + 38}
                                className={`text-xs ${isSelected ? "fill-blue-700" : "fill-gray-600"}`}
                            >
                                {pkg.rules.length} règle{pkg.rules.length !== 1 ? 's' : ''}
                            </text>

                            {/* Condition (si présente) */}
                            {isConditional && pkg.condition && (
                                <text
                                    x={pkg.x + 35}
                                    y={currentY + 56}
                                    className="text-xs fill-amber-700"
                                >
                                    if {pkg.condition.length > 25 ? pkg.condition.substring(0, 25) + '...' : pkg.condition}
                                </text>
                            )}

                        </g>
                    );
                })}

                {/* Ligne pointillée entre dernier package et END */}
                {diagramData.length > 0 && lastPackageY !== null && (
                    <line
                        x1={centerX}
                        y1={lastPackageY + packageHeight}
                        x2={centerX}
                        y2={lastPackageY + packageHeight + 40}
                        stroke="#d1d5db"
                        strokeWidth="2"
                        strokeDasharray="5,5"
                    />
                )}

                {/* Point de fin */}
                <g>
                    <circle
                        cx={centerX}
                        cy={endBaseY + 52}
                        r="12"
                        fill="#ef4444"
                        filter="url(#drop-shadow)"
                    />
                    <text
                        x={centerX}
                        y={endBaseY + 57}
                        textAnchor="middle"
                        className="fill-white text-xs font-bold"
                    >
                        ◼
                    </text>
                    <text
                        x={centerX}
                        y={endBaseY + 77}
                        textAnchor="middle"
                        className="fill-gray-600 text-xs font-medium"
                    >
                        END
                    </text>
                </g>

                {/* Légende déplaçable */}
                {showLegend && (
                    <g
                        ref={legendRef}
                        transform={`translate(${legendPosition.x}, ${legendPosition.y})`}
                        onMouseDown={handleLegendMouseDown}
                        style={{ cursor: isLegendDragging ? 'grabbing' : 'grab' }}
                    >
                        <rect
                            x="0"
                            y="0"
                            width="250"
                            height="25"
                            rx="4"
                            fill="white"
                            stroke="#e5e7eb"
                            fillOpacity="0.95"
                            className="hover:stroke-blue-300 transition-colors"
                        />
                        <text x="8" y="16" className="fill-gray-600 text-xs font-medium pointer-events-none">
                            💡 Clic sur un package pour l'éditer
                        </text>
                        {/* Bouton de fermeture */}
                        <g
                            onClick={(e) => {
                                e.stopPropagation();
                                setShowLegend(false);
                            }}
                            className="cursor-pointer"
                        >
                            <circle
                                cx="240"
                                cy="12.5"
                                r="8"
                                fill="#ef4444"
                                className="hover:fill-red-600 transition-colors"
                            />
                            <text
                                x="240"
                                y="16"
                                textAnchor="middle"
                                className="fill-white text-xs font-bold pointer-events-none"
                            >
                                ×
                            </text>
                        </g>
                    </g>
                )}
            </svg>
        </div>
    );
}
