import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url);
        const app = searchParams.get('app');
        const runtime = searchParams.get('runtime');

        if (!app || !runtime) {
            return NextResponse.json(
                { error: 'Paramètres app et runtime requis' },
                { status: 400 }
            );
        }

        // Appeler l'API backend pour convertir decision_engine.py en JSON
        const backendUrl = process.env.BACKEND_URL || 'http://localhost:8002';
        const response = await fetch(
            `${backendUrl}/api/v1/ruleflow/runtime/${encodeURIComponent(runtime)}/apps/${encodeURIComponent(app)}/config`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Erreur API backend:', errorText);
            return NextResponse.json(
                { error: `Erreur lors du chargement: ${response.status} ${errorText}` },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);

    } catch (error) {
        console.error('Erreur lors du chargement de la configuration:', error);
        return NextResponse.json(
            { error: `Erreur lors du chargement de la configuration: ${error instanceof Error ? error.message : String(error)}` },
            { status: 500 }
        );
    }
}