import { useEffect, useRef } from "react";

import { initBackground } from "../background/initBackground.ts";

export default function Background() {
	const ref = useRef<HTMLCanvasElement>(null);

	useEffect(() => {
		if (!ref.current) return;
		return initBackground(ref.current);
	}, []);

	return <canvas id="bg" aria-hidden="true" ref={ref} />;
}
