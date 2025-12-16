import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        const { config } = await request.json();

        if (!config || !config.metadata) {
            return NextResponse.json(
                { error: 'Configuration invalide' },
                { status: 400 }
            );
        }

        // Appeler le service backend pour générer le code Python
        const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

        const response = await fetch(`${backendUrl}/api/ruleflow/generate-from-config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ config })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Erreur backend: ${response.status} - ${errorText}`);
        }

        const result = await response.json();

        return NextResponse.json({
            success: true,
            message: 'Code généré avec succès',
            generatedCode: result.generated_code,
            filePath: result.file_path
        });

    } catch (error) {
        console.error('Erreur lors de la génération du code:', error);
        return NextResponse.json(
            { error: `Erreur lors de la génération du code: ${error instanceof Error ? error.message : 'Unknown error'}` },
            { status: 500 }
        );
    }
}