import React from "react";

import { initBackground } from "../background/initBackground.ts";

export default function Background() {
    const ref = React.useRef<HTMLCanvasElement>(null);

    React.useEffect(() => {
        if (!ref.current) return;
        return initBackground(ref.current);
    }, []);

    return <canvas id="bg" aria-hidden="true" ref={ref} />;
}
