import {
	GREEN,
	CELL,
	DOT,
	BASE,
	WAVE,
	BLOB,
	BLOB_RADIUS,
	POINTER,
	POINTER_RADIUS,
	BLOBS,
} from "./config.js";

export function initBackground(canvas) {
	if (!canvas) return;

	const ctx = canvas.getContext("2d");
	const reduceMotion = window.matchMedia(
		"(prefers-reduced-motion: reduce)",
	).matches;

	let cols = 0;
	let rows = 0;
	let dpr = 1;

	const pointer = { x: -9999, y: -9999, active: false };

	function resize() {
		dpr = Math.min(window.devicePixelRatio || 1, 2);

		const w = window.innerWidth;
		const h = window.innerHeight;

		canvas.width = Math.floor(w * dpr);
		canvas.height = Math.floor(h * dpr);

		canvas.style.width = w + "px";
		canvas.style.height = h + "px";

		ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

		cols = Math.ceil(w / CELL) + 1;
		rows = Math.ceil(h / CELL) + 1;
	}

	function draw(time) {
		const t = time * 0.0006;
		const ts = time * 0.001;

		const w = window.innerWidth;
		const h = window.innerHeight;

		ctx.clearRect(0, 0, w, h);

		const bx = [];
		const by = [];

		for (let i = 0; i < BLOBS.length; i++) {
			const b = BLOBS[i];
			bx[i] = (0.5 + b.ax * Math.sin(ts * b.fx + b.px)) * w;
			by[i] = (0.5 + b.ay * Math.sin(ts * b.fy + b.py)) * h;
		}

		const r2 = BLOB_RADIUS * BLOB_RADIUS;

		for (let r = 0; r < rows; r++) {
			for (let c = 0; c < cols; c++) {
				const x = c * CELL;
				const y = r * CELL;

				const wave =
					Math.sin(c * 0.35 + t) * 0.5 + Math.sin(r * 0.45 + t * 0.8) * 0.5;
				let alpha = BASE + WAVE * (wave * 0.5 + 0.5);

				for (let i = 0; i < BLOBS.length; i++) {
					const dx = x - bx[i];
					const dy = y - by[i];

					const dd = dx * dx + dy * dy;

					if (dd < r2) {
						const f = 1 - Math.sqrt(dd) / BLOB_RADIUS;
						alpha += BLOB * f * f;
					}
				}

				if (pointer.active) {
					const dx = x - pointer.x;
					const dy = y - pointer.y;

					const dist = Math.sqrt(dx * dx + dy * dy);

					if (dist < POINTER_RADIUS) {
						alpha += POINTER * (1 - dist / POINTER_RADIUS);
					}
				}

				if (alpha < 0.012) continue;
				if (alpha > 0.75) alpha = 0.75;

				ctx.fillStyle = `rgba(${GREEN[0]}, ${GREEN[1]}, ${GREEN[2]}, ${alpha})`;
				ctx.fillRect(x, y, DOT, DOT);
			}
		}
	}

	function drawStatic() {
		const w = window.innerWidth;
		const h = window.innerHeight;

		ctx.clearRect(0, 0, w, h);

		for (let r = 0; r < rows; r++) {
			for (let c = 0; c < cols; c++) {
				ctx.fillStyle = `rgba(${GREEN[0]}, ${GREEN[1]}, ${GREEN[2]}, ${BASE})`;
				ctx.fillRect(c * CELL, r * CELL, DOT, DOT);
			}
		}
	}

	let raf = 0;
	function loop(time) {
		draw(time);
		raf = requestAnimationFrame(loop);
	}

	window.addEventListener("resize", () => {
		resize();
		if (reduceMotion) drawStatic();
	});

	window.addEventListener(
		"pointermove",
		(e) => {
			pointer.x = e.clientX;
			pointer.y = e.clientY;
			pointer.active = true;
		},
		{ passive: true },
	);
	window.addEventListener("pointerleave", () => (pointer.active = false));

	document.addEventListener("visibilitychange", () => {
		if (document.hidden) {
			cancelAnimationFrame(raf);
			raf = 0;
		} else if (!reduceMotion && !raf) {
			raf = requestAnimationFrame(loop);
		}
	});

	resize();

	if (reduceMotion) {
		drawStatic();
	} else {
		raf = requestAnimationFrame(loop);
	}
}
