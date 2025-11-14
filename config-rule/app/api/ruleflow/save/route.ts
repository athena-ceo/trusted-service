import { NextRequest, NextResponse } from 'next/server';
import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';

export async function POST(request: NextRequest) {
    try {
        const { config } = await request.json();

        if (!config || !config.metadata) {
            return NextResponse.json(
                { error: 'Configuration invalide' },
                { status: 400 }
            );
        }

        const { app_name, runtime } = config.metadata;

        // Chemin vers le répertoire de l'app
        const appDir = join(
            process.cwd(),
            '..',
            runtime,
            'apps',
            app_name
        );

        // Créer le répertoire si nécessaire
        if (!existsSync(appDir)) {
            mkdirSync(appDir, { recursive: true });
        }

        // Chemin vers le fichier de configuration
        const configPath = join(appDir, 'ruleflow-config.json');

        // Sauvegarder la configuration JSON
        writeFileSync(configPath, JSON.stringify(config, null, 2));

        return NextResponse.json({
            success: true,
            message: 'Configuration sauvegardée',
            path: configPath
        });

    } catch (error) {
        console.error('Erreur lors de la sauvegarde:', error);
        return NextResponse.json(
            { error: 'Erreur lors de la sauvegarde de la configuration' },
            { status: 500 }
        );
    }
}