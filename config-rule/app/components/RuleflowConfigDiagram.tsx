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
    // Largeur augmentée pour accommoder les branches conditionnelles (150px de décalage + 200px de package + 20px d'espace)
    const svgWidth = 650; // Largeur augmentée pour les branches "oui" des conditions
    const centerX = svgWidth / 2 - 150;
    const packageWidth = 200;
    const packageHeight = 80;
    const startY = 140; // Décalage initial pour laisser de la place au START
    const decisionDiamondSize = 70; // Taille du losange de décision (augmentée pour meilleure lisibilité)
    const branchOffset = 150; // Décalage horizontal pour la branche "oui" (augmenté pour plus d'espace)
    const horizontalSpacing = 20; // Espacement horizontal entre le losange et le package conditionnel
    const arrowGap = 20; // Espace pour la petite flèche avant le losange
    const connectorStartOffset = 10; // Décale le début de la ligne sous le package précédent

    const diagramData = useMemo(() => {
        // Trier les packages par ordre d'exécution
        const sortedPackages = [...packages].sort((a, b) => a.execution_order - b.execution_order);

        const packageX = centerX - packageWidth / 2; // Centrer le package
        const verticalSpacing = 130; // Espacement vertical de base (augmenté)
        const conditionalSpacing = 220; // Espacement supplémentaire pour les packages conditionnels (augmenté)
        const decisionOffset = 80; // Distance entre le losange et le package (augmenté pour éviter le chevauchement)

        // Calculer les positions des packages avec espacement pour les conditions
        let currentY = startY;
        const packagePositions = sortedPackages.map((pkg, index) => {
            const hasCondition = pkg.condition !== null && pkg.condition !== '';
            const previousHasCondition = index > 0 && sortedPackages[index - 1].condition !== null && sortedPackages[index - 1].condition !== '';

            // Espacement supplémentaire si le package précédent avait une condition
            if (previousHasCondition) {
                currentY += 80; // Espace pour la jonction après le package conditionnel (augmenté)
            }

            const packageY = hasCondition ? currentY + 60 : currentY; // Décaler les packages conditionnels de 60px vers le bas
            const decisionY = hasCondition ? packageY - decisionOffset : null; // Losange au-dessus du package avec espacement

            // Espacement pour le prochain package
            if (hasCondition) {
                currentY += conditionalSpacing; // Plus d'espace pour les branches
            } else {
                currentY += verticalSpacing;
            }

            return {
                ...pkg,
                x: packageX,
                y: packageY,
                width: packageWidth,
                height: packageHeight,
                centerX: centerX,
                hasCondition,
                decisionY,
                decisionX: centerX,
                decisionSize: decisionDiamondSize,
                branchOffset: hasCondition ? branchOffset : 0,
                mergeY: hasCondition ? packageY + packageHeight + 80 : null, // Point de jonction après le package (augmenté)
                packageXRight: hasCondition ? centerX + decisionDiamondSize / 2 + horizontalSpacing : null // Position X du package sur la branche "oui"
            };
        });

        return packagePositions;
    }, [packages, centerX, packageWidth, packageHeight, startY, decisionDiamondSize, branchOffset, horizontalSpacing]);

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

    // Calculer la hauteur du SVG en tenant compte des conditions (doit être calculé avant handleMouseMove)
    const firstPackageCalc = diagramData[0];
    const lastPackageCalc = diagramData[diagramData.length - 1];
    const lastPackageHasConditionCalc = lastPackageCalc?.hasCondition ?? false;
    const endBaseYCalc = lastPackageHasConditionCalc && lastPackageCalc?.mergeY
        ? lastPackageCalc.mergeY
        : (lastPackageCalc?.y ?? 128) + packageHeight;

    const maxYCalc = Math.max(
        ...diagramData.map(pkg => {
            if (pkg.hasCondition && pkg.mergeY) {
                return pkg.mergeY;
            }
            return pkg.y + packageHeight;
        }),
        endBaseYCalc
    );
    const svgHeightCalc = Math.max(400, maxYCalc + 100);

    const handleMouseMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
        const svgPoint = getSvgPoint(e);
        if (!svgPoint) return;

        if (isLegendDragging) {
            const newX = svgPoint.x - legendDragOffset.x;
            const newY = svgPoint.y - legendDragOffset.y;

            // Limiter la position dans les limites du SVG
            const maxX = svgWidth - 200; // largeur SVG - largeur légende
            const maxY = svgHeightCalc - 25; // hauteur SVG - hauteur légende

            setLegendPosition({
                x: Math.max(0, Math.min(newX, maxX)),
                y: Math.max(0, Math.min(newY, maxY))
            });
        }

        if (draggingPackage) {
            const proposedY = svgPoint.y - draggingPackage.offsetY;
            const minY = startY - packageHeight;
            const maxY = svgHeightCalc - packageHeight - 40;
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
    }, [computeInsertIndex, draggingPackage, getSvgPoint, isLegendDragging, legendDragOffset, svgHeightCalc, svgWidth, startY, packageHeight]);

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
    const lastPackageHasCondition = lastPackage?.hasCondition ?? false;
    const endBaseY = lastPackageHasCondition && lastPackage?.mergeY
        ? lastPackage.mergeY
        : (lastPackageY ?? 128) + packageHeight;

    // Utiliser la hauteur calculée précédemment
    const svgHeight = svgHeightCalc;

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
                {/* Flèche simple depuis START vers premier package ou décision */}
                {diagramData.length > 0 && firstPackageY !== null && (
                    <>
                        {diagramData[0].hasCondition && diagramData[0].decisionY !== null ? (
                            // Flèche vers le losange de décision
                            <line
                                x1={centerX}
                                y1={firstPackageY - 20}
                                x2={centerX}
                                y2={diagramData[0].decisionY! + decisionDiamondSize / 2}
                                stroke="#6b7280"
                                strokeWidth="2"
                                markerEnd="url(#arrowhead)"
                            />
                        ) : (
                            // Flèche directe vers le package
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
                    </>
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

                {/* Packages et décisions */}
                {diagramData.map((pkg, index) => {
                    const isLocked = pkg.name === LOCKED_PACKAGE_NAME;
                    const isSelected = selectedPackage === pkg.id;
                    const isConditional = pkg.hasCondition;
                    const previousPackage = index > 0 ? diagramData[index - 1] : null;
                    const currentY = resolvePackageY(pkg.id, pkg.y);
                    const previousY = previousPackage ? resolvePackageY(previousPackage.id, previousPackage.y) : null;
                    const previousMergeY = previousPackage?.hasCondition ? previousPackage.mergeY : null;
                    const isDraggable = Boolean(onReorderPackage);
                    const decisionY = pkg.decisionY;
                    const packageXRight = pkg.packageXRight ?? pkg.x;

                    return (
                        <g key={pkg.id}>
                            {/* Flèche depuis le bas du package précédent */}
                            {previousPackage && previousY !== null && (
                                <>
                                    {/* Flèche directe depuis le bas du package précédent (même si le package précédent a une condition) */}
                                    <line
                                        x1={centerX}
                                        y1={previousY + packageHeight + connectorStartOffset}
                                        x2={centerX}
                                        y2={isConditional && decisionY !== null ? decisionY - arrowGap : currentY - arrowGap}
                                        stroke="#6b7280"
                                        strokeWidth="2"
                                    />
                                    {/* Petite flèche avant le losange si conditionnel */}
                                    {isConditional && decisionY !== null && (
                                        <line
                                            x1={centerX}
                                            y1={decisionY - arrowGap}
                                            x2={centerX}
                                            y2={decisionY + decisionDiamondSize / 2}
                                            stroke="#6b7280"
                                            strokeWidth="2"
                                            markerEnd="url(#arrowhead)"
                                        />
                                    )}
                                    {/* Flèche vers le package si non conditionnel */}
                                    {!isConditional && (
                                        <line
                                            x1={centerX}
                                            y1={currentY - arrowGap}
                                            x2={centerX}
                                            y2={currentY}
                                            stroke="#6b7280"
                                            strokeWidth="2"
                                            markerEnd="url(#arrowhead)"
                                        />
                                    )}
                                </>
                            )}

                            {/* Losange de décision (si condition) */}
                            {isConditional && decisionY !== null && pkg.condition && (
                                <g>
                                    {/* Texte de la condition simplifiée à gauche du losange */}
                                    <text
                                        x={centerX - decisionDiamondSize / 2 - 10}
                                        y={decisionY + decisionDiamondSize / 2 + 4}
                                        textAnchor="end"
                                        className="fill-gray-900 text-xs font-semibold"
                                    >
                                        {(() => {
                                            const simplified = simplifyCondition(pkg.condition);
                                            return simplified.length > 25 ? simplified.substring(0, 25) + '...' : simplified;
                                        })()}
                                    </text>

                                    {/* Losange avec meilleur style */}
                                    <polygon
                                        points={`
                                            ${centerX},${decisionY} 
                                            ${centerX + decisionDiamondSize / 2},${decisionY + decisionDiamondSize / 2} 
                                            ${centerX},${decisionY + decisionDiamondSize} 
                                            ${centerX - decisionDiamondSize / 2},${decisionY + decisionDiamondSize / 2}
                                        `}
                                        fill="#fff9e6"
                                        stroke="#f59e0b"
                                        strokeWidth="2.5"
                                        filter="url(#drop-shadow)"
                                    />

                                    {/* Branche "oui" (vers la droite puis vers le milieu du haut du package) */}
                                    {packageXRight !== null && (
                                        <>
                                            <path
                                                d={`M ${centerX + decisionDiamondSize / 2} ${decisionY + decisionDiamondSize / 2} 
                                                    L ${packageXRight + packageWidth / 2} ${decisionY + decisionDiamondSize / 2} 
                                                    L ${packageXRight + packageWidth / 2} ${currentY}`}
                                                fill="none"
                                                stroke="#6b7280"
                                                strokeWidth="2"
                                                markerEnd="url(#arrowhead)"
                                            />
                                            {/* Label "oui" avec fond */}
                                            <rect
                                                x={centerX + decisionDiamondSize / 2 + 8}
                                                y={decisionY + decisionDiamondSize / 2 - 12}
                                                width="28"
                                                height="16"
                                                rx="3"
                                                fill="white"
                                                stroke="#6b7280"
                                                strokeWidth="1"
                                            />
                                            <text
                                                x={centerX + decisionDiamondSize / 2 + 22}
                                                y={decisionY + decisionDiamondSize / 2 - 2}
                                                textAnchor="middle"
                                                className="fill-gray-700 text-xs font-semibold"
                                            >
                                                oui
                                            </text>
                                        </>
                                    )}

                                    {/* Branche "non" (vers le bas, contourne le package) - sans flèche de fin */}
                                    <path
                                        d={`M ${centerX} ${decisionY + decisionDiamondSize} 
                                            L ${centerX} ${pkg.mergeY ?? currentY + packageHeight + 40}`}
                                        fill="none"
                                        stroke="#6b7280"
                                        strokeWidth="2"
                                    />
                                    {/* Label "non" avec fond */}
                                    <rect
                                        x={centerX + 8}
                                        y={decisionY + decisionDiamondSize + 8}
                                        width="28"
                                        height="16"
                                        rx="3"
                                        fill="white"
                                        stroke="#6b7280"
                                        strokeWidth="1"
                                    />
                                    <text
                                        x={centerX + 22}
                                        y={decisionY + decisionDiamondSize + 20}
                                        textAnchor="middle"
                                        className="fill-gray-700 text-xs font-semibold"
                                    >
                                        non
                                    </text>

                                    {/* Ligne de retour depuis le milieu du bas du package vers le point de jonction - arrive exactement sur le point */}
                                    {pkg.mergeY !== null && packageXRight !== null && (
                                        <path
                                            d={`M ${packageXRight + packageWidth / 2} ${currentY + packageHeight} 
                                                L ${packageXRight + packageWidth / 2} ${pkg.mergeY - 24} 
                                                L ${centerX} ${pkg.mergeY - 24} 
                                                L ${centerX} ${pkg.mergeY}`}
                                            fill="none"
                                            stroke="#6b7280"
                                            strokeWidth="2"
                                        />
                                    )}

                                    {/* Point de jonction visible (sans flèche) */}
                                    {pkg.mergeY !== null && (
                                        <circle
                                            cx={centerX}
                                            cy={pkg.mergeY}
                                            r="4"
                                            fill="#6b7280"
                                        />
                                    )}
                                </g>
                            )}

                            {/* Rectangle principal du package */}
                            <g
                                className={isDraggable && !isLocked ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer'}
                                onMouseDown={isDraggable && !isLocked ? handlePackageMouseDown(pkg.id, index, currentY, isLocked) : undefined}
                            >
                                <rect
                                    x={isConditional ? (packageXRight ?? pkg.x) : pkg.x}
                                    y={currentY}
                                    width={pkg.width}
                                    height={pkg.height}
                                    rx="8"
                                    fill={isSelected ? "#dbeafe" : "#ffffff"}
                                    stroke={isSelected ? "#3b82f6" : isConditional ? "#f59e0b" : "#d1d5db"}
                                    strokeWidth={isSelected ? "3" : "2.5"}
                                    className={`${isDraggable && !isLocked ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer'} hover:stroke-blue-400 transition-colors`}
                                    filter="url(#drop-shadow)"
                                    onClick={() => handlePackageClick(pkg.id)}
                                />

                                {/* Numéro d'ordre */}
                                <circle
                                    cx={(isConditional ? (packageXRight ?? pkg.x) : pkg.x) + 15}
                                    cy={currentY + 15}
                                    r="11"
                                    fill={isSelected ? "#3b82f6" : "#6b7280"}
                                />
                                <text
                                    x={(isConditional ? (packageXRight ?? pkg.x) : pkg.x) + 15}
                                    y={currentY + 21}
                                    textAnchor="middle"
                                    className="fill-white text-xs font-bold"
                                >
                                    {index + 1}
                                </text>

                                {/* Nom du package */}
                                <text
                                    x={(isConditional ? (packageXRight ?? pkg.x) : pkg.x) + 35}
                                    y={currentY + 22}
                                    className={`text-sm font-semibold ${isSelected ? "fill-blue-900" : "fill-gray-900"}`}
                                >
                                    {formatPackageName(pkg.name)}
                                </text>

                                {/* Nombre de règles */}
                                <text
                                    x={(isConditional ? (packageXRight ?? pkg.x) : pkg.x) + 35}
                                    y={currentY + 40}
                                    className={`text-xs ${isSelected ? "fill-blue-700" : "fill-gray-600"}`}
                                >
                                    {pkg.rules.length} règle{pkg.rules.length !== 1 ? 's' : ''}
                                </text>
                            </g>
                        </g>
                    );
                })}

                {/* Ligne pointillée entre dernier package et END */}
                {diagramData.length > 0 && (
                    <line
                        x1={centerX}
                        y1={endBaseY}
                        x2={centerX}
                        y2={endBaseY + 40}
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
