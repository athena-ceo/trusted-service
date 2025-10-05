"use client";

import React from 'react';
import { Button } from "@carbon/react";
import { Minimize, Maximize } from "@carbon/icons-react";

interface WatsonExpandButtonProps {
    isExpanded: boolean;
    onClick: (e: React.MouseEvent) => void;
}

const WatsonExpandButton: React.FC<WatsonExpandButtonProps> = ({ isExpanded, onClick }) => {
    return (
        <Button
            hasIconOnly
            kind="ghost"
            size="sm"
            tooltipAlignment="end"
            tooltipDropShadow
            tooltipHighContrast
            tooltipPosition="bottom"
            className="watson-expand-btn"
            onClick={onClick}
            renderIcon={isExpanded ? Minimize : Maximize}
            iconDescription={isExpanded ? "Restore chat" : "Maximize chat"}
            style={{
                position: 'relative',
                zIndex: 1
            }}
        />
    );
};

export default WatsonExpandButton;