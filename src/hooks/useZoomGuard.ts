import { useEffect } from "react";

export function useZoomGuard(): void {
    useEffect(() => {
        const onGesture = (e: Event) => e.preventDefault();
        const gestureTypes = ["gesturestart", "gesturechange", "gestureend"];
        gestureTypes.forEach((type) =>
            document.addEventListener(type, onGesture, { passive: false }),
        );

        let lastTouchEnd = 0;
        const onTouchEnd = (e: TouchEvent) => {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) e.preventDefault();
            lastTouchEnd = now;
        };
        document.addEventListener("touchend", onTouchEnd, { passive: false });

        const onWheel = (e: WheelEvent) => {
            if (e.ctrlKey) e.preventDefault();
        };
        document.addEventListener("wheel", onWheel, { passive: false });

        const onKeyDown = (e: KeyboardEvent) => {
            if (
                (e.ctrlKey || e.metaKey) &&
                ["+", "-", "=", "0"].includes(e.key)
            ) {
                e.preventDefault();
            }
        };
        document.addEventListener("keydown", onKeyDown);

        return () => {
            gestureTypes.forEach((type) =>
                document.removeEventListener(type, onGesture),
            );
            document.removeEventListener("touchend", onTouchEnd);
            document.removeEventListener("wheel", onWheel);
            document.removeEventListener("keydown", onKeyDown);
        };
    }, []);
}
