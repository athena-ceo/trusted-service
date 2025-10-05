"use client";

import { createRoot } from "react-dom/client";
import WatsonExpandButton from "@/components/WatsonExpandButton";

// Fonction utilitaire pour observer et injecter le bouton Watson
const setupWatsonButtonObserver = (createExpandButton: () => HTMLElement) => {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const element = node as Element;

                    // Chercher la barre d'actions Watson
                    const headerActions = element.querySelectorAll('.wxoLiteHeaderActions');
                    headerActions.forEach((headerAction) => {
                        // Vérifier qu'on n'a pas déjà ajouté un bouton
                        if (!headerAction.querySelector('.watson-expand-btn-container')) {
                            const expandButton = createExpandButton();

                            // Cibler les bons éléments selon la structure HTML réelle
                            const aiLabelDiv = headerAction.querySelector('.wxoLiteHeaderLable');
                            const minimizeButtonWrapper = headerAction.querySelector('.cds--tooltip.cds--icon-tooltip');

                            if (aiLabelDiv && minimizeButtonWrapper) {
                                // Insérer le bouton entre la div AI et le wrapper du bouton minimizer
                                headerAction.insertBefore(expandButton, minimizeButtonWrapper);
                            } else if (minimizeButtonWrapper) {
                                // Fallback : insérer avant le wrapper du bouton minimizer
                                headerAction.insertBefore(expandButton, minimizeButtonWrapper);
                            } else {
                                // Fallback final : ajouter à la fin
                                headerAction.appendChild(expandButton);
                            }
                        }
                    });
                }
            });
        });
    });

    // Démarrer l'observation
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    return observer;
};

export const useWatsonExpandButton = () => {
    const createExpandButton = () => {
        // Créer un conteneur pour le composant React
        const container = document.createElement('div');
        container.className = 'watson-expand-btn-container';

        let isExpanded = false;
        let root: any = null;

        // Fonction pour gérer le clic sur le bouton
        const handleClick = (e: React.MouseEvent) => {
            e.stopPropagation();

            const wxoFloat = document.querySelector('.wxo-float') as HTMLElement;

            if (!isExpanded) {
                // Logique d'expansion
                if (wxoFloat) {
                    wxoFloat.dataset.originalWidth = wxoFloat.style.width || getComputedStyle(wxoFloat).width;
                    wxoFloat.dataset.originalHeight = wxoFloat.style.height || getComputedStyle(wxoFloat).height;
                    wxoFloat.dataset.originalBottom = wxoFloat.style.bottom || getComputedStyle(wxoFloat).bottom;
                    wxoFloat.dataset.originalRight = wxoFloat.style.right || getComputedStyle(wxoFloat).right;
                    wxoFloat.dataset.originalTop = wxoFloat.style.top || getComputedStyle(wxoFloat).top;
                    wxoFloat.dataset.originalLeft = wxoFloat.style.left || getComputedStyle(wxoFloat).left;

                    const maxWidth = Math.min(window.innerWidth * 0.9, 1600);
                    const maxHeight = Math.min(window.innerHeight * 0.9, 900);

                    wxoFloat.style.setProperty('width', `${maxWidth}px`, 'important');
                    wxoFloat.style.setProperty('height', `${maxHeight}px`, 'important');
                    wxoFloat.style.setProperty('top', '20px', 'important');
                    wxoFloat.style.setProperty('right', '20px', 'important');
                    wxoFloat.style.setProperty('bottom', 'auto', 'important');
                    wxoFloat.style.setProperty('left', 'auto', 'important');
                    wxoFloat.style.removeProperty('transform');
                    wxoFloat.style.setProperty('z-index', '9999', 'important');
                }

                isExpanded = true;
            } else {
                // Logique de réduction
                if (wxoFloat) {
                    if (wxoFloat.dataset.originalWidth) {
                        wxoFloat.style.setProperty('width', wxoFloat.dataset.originalWidth, 'important');
                    } else {
                        wxoFloat.style.removeProperty('width');
                    }
                    if (wxoFloat.dataset.originalHeight) {
                        wxoFloat.style.setProperty('height', wxoFloat.dataset.originalHeight, 'important');
                    } else {
                        wxoFloat.style.removeProperty('height');
                    }

                    wxoFloat.style.removeProperty('top');
                    wxoFloat.style.removeProperty('left');
                    wxoFloat.style.removeProperty('transform');

                    if (wxoFloat.dataset.originalBottom) {
                        wxoFloat.style.setProperty('bottom', wxoFloat.dataset.originalBottom, 'important');
                    } else {
                        wxoFloat.style.setProperty('bottom', '0px', 'important');
                    }
                    if (wxoFloat.dataset.originalRight) {
                        wxoFloat.style.setProperty('right', wxoFloat.dataset.originalRight, 'important');
                    } else {
                        wxoFloat.style.setProperty('right', '0px', 'important');
                    }
                }

                isExpanded = false;
            }

            // Re-render le bouton pour mettre à jour l'icône et le tooltip
            renderButton();
        };

        // Fonction pour re-render le bouton
        const renderButton = () => {
            if (root) {
                root.render(<WatsonExpandButton isExpanded={isExpanded} onClick={handleClick} />);
            } else {
                root = createRoot(container);
                root.render(<WatsonExpandButton isExpanded={isExpanded} onClick={handleClick} />);
            }
        };

        // Render initial
        renderButton();

        // Stocker la fonction de mise à jour sur le conteneur pour y accéder plus tard
        (container as any).updateButton = (newIsExpanded: boolean) => {
            isExpanded = newIsExpanded;
            renderButton();
        };

        return container;
    };

    return { createExpandButton, setupWatsonButtonObserver };
};