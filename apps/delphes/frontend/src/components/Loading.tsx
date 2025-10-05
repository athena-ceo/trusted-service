import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import "@/app/spinner.css";

interface LoadingProps {
    message?: string;
    showBackButton?: boolean;
    backButtonText?: string;
    backButtonHref?: string;
}

export default function Loading({
    message = "Chargement...",
    showBackButton = true,
    backButtonText = "Retour à l'accueil",
    backButtonHref = "/"
}: LoadingProps) {
    return (
        <>
            <Header />
            <main role="main" id="main" className="fr-container fr-py-6w">
                <div className="fr-grid-row fr-grid-row--gutters">
                    <div className="fr-col-12 fr-col-md-8 fr-col-offset-md-2">
                        <div className="fr-alert fr-alert--info fr-mb-4w">
                            <h1 className="fr-alert__title">{message}</h1>
                            <p>Veuillez patienter pendant que nous traitons votre demande...</p>
                        </div>

                        <div className="fr-grid-row fr-grid-row--center fr-mt-3w">
                            <div className="fr-col-auto">
                                <div className="fr-spinner fr-spinner--lg"></div>
                            </div>
                        </div>

                        {showBackButton && (
                            <div className="fr-col-12 fr-mt-10w">
                                <Link href={backButtonHref} className="fr-btn fr-mr-2w">
                                    {backButtonText}
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </main>
            <Footer />
        </>
    );
}