import Background from "../components/Background.tsx";
import { useZoomGuard } from "../hooks/useZoomGuard.ts";

export default function Landing() {
    useZoomGuard();

    return (
        <>
            <Background />
            <main className="stage">
                <h1>
                    colloqq<span className="green">.tech</span>
                </h1>
                <p className="tagline">Мы уже работаем над ним.</p>
                <div className="status">В разработке</div>
            </main>
        </>
    );
}
