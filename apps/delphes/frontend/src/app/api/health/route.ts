import { NextResponse } from 'next/server';

/**
 * Health check endpoint for Docker healthchecks and monitoring
 * Returns a simple JSON response indicating service status
 */
export async function GET() {
    return NextResponse.json(
        {
            status: 'ok',
            timestamp: new Date().toISOString(),
            service: 'delphes-frontend'
        },
        { status: 200 }
    );
}
