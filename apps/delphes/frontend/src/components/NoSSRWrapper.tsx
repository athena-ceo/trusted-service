"use client";

import dynamic from 'next/dynamic';
import { ReactNode } from 'react';

interface NoSSRWrapperProps {
    children: ReactNode;
    fallback?: ReactNode;
}

const NoSSRWrapper = ({ children, fallback }: NoSSRWrapperProps) => {
    return <>{children}</>;
};

export default dynamic(() => Promise.resolve(NoSSRWrapper), {
    ssr: false,
    loading: () => (
        <div className="fr-container fr-py-6w">
            <div className="fr-grid-row fr-grid-row--center">
                <div className="fr-col-12 fr-col-md-6">
                    <p>Chargement...</p>
                </div>
            </div>
        </div>
    ),
});