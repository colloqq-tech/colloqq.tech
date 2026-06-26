import {
    BASE,
    BLOB,
    BLOB_MAG,
    BLOB_RADIUS,
    BLOB_REFRACT,
    BLOBS,
    CELL,
    DOT,
    GREEN,
    POINTER,
    POINTER_FOLLOW,
    POINTER_GROW,
    POINTER_MAG,
    POINTER_RADIUS,
    POINTER_REFRACT,
    WAVE,
} from "./config.ts";

export function initBackground(canvas: HTMLCanvasElement): () => void {
    const ctx = canvas.getContext("2d");
    if (!ctx) return () => {};

    const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
    ).matches;

    let cols = 0;
    let rows = 0;
    let dpr = 1;

    const pointer = { x: -9999, y: -9999, active: false };

    const lens = { x: 0, y: 0, grow: 0, seeded: false };
    let lastTime = 0;

    function resize() {
        dpr = Math.min(window.devicePixelRatio || 1, 2);

        const w = window.innerWidth;
        const h = window.innerHeight;

        canvas.width = Math.floor(w * dpr);
        canvas.height = Math.floor(h * dpr);

        canvas.style.width = w + "px";
        canvas.style.height = h + "px";

        ctx!.setTransform(dpr, 0, 0, dpr, 0, 0);

        cols = Math.ceil(w / CELL) + 1;
        rows = Math.ceil(h / CELL) + 1;
    }

    function draw(time: number) {
        const t = time * 0.0006;
        const ts = time * 0.001;

        const dt = lastTime ? Math.min((time - lastTime) / 1000, 0.05) : 0;
        lastTime = time;

        if (pointer.active) {
            if (!lens.seeded) {
                lens.x = pointer.x;
                lens.y = pointer.y;
                lens.seeded = true;
            }
            const k = 1 - Math.exp(-POINTER_FOLLOW * dt);
            lens.x += (pointer.x - lens.x) * k;
            lens.y += (pointer.y - lens.y) * k;
            lens.grow += (1 - lens.grow) * (1 - Math.exp(-POINTER_GROW * dt));
        } else {
            lens.grow += (0 - lens.grow) * (1 - Math.exp(-POINTER_GROW * dt));
            if (lens.grow < 0.001) {
                lens.grow = 0;
                lens.seeded = false;
            }
        }

        const w = window.innerWidth;
        const h = window.innerHeight;

        ctx!.clearRect(0, 0, w, h);

        const bx: number[] = [];
        const by: number[] = [];

        for (let i = 0; i < BLOBS.length; i++) {
            const b = BLOBS[i];
            bx[i] = (0.5 + b.ax * Math.sin(ts * b.fx + b.px)) * w;
            by[i] = (0.5 + b.ay * Math.sin(ts * b.fy + b.py)) * h;
        }

        const r2 = BLOB_RADIUS * BLOB_RADIUS;
        const acc = { dx: 0, dy: 0, mag: 1 };

        function applyLens(
            x: number,
            y: number,
            cx: number,
            cy: number,
            dist: number,
            radius: number,
            refract: number,
            magnify: number,
            g: number,
        ) {
            const nd = dist / radius;

            const bent = Math.pow(nd, refract);
            const eND = nd + (bent - nd) * g;

            if (dist > 0.0001) {
                const ux = (x - cx) / dist;
                const uy = (y - cy) / dist;
                acc.dx += cx + ux * eND * radius - x;
                acc.dy += cy + uy * eND * radius - y;
            }

            const ring = Math.cos(nd * Math.PI);
            acc.mag *= 1 + (magnify - 1) * g * Math.max(ring, -0.35);
        }

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const x = c * CELL;
                const y = r * CELL;

                acc.dx = 0;
                acc.dy = 0;
                acc.mag = 1;

                const wave =
                    Math.sin(c * 0.35 + t) * 0.5 +
                    Math.sin(r * 0.45 + t * 0.8) * 0.5;
                let alpha = BASE + WAVE * (wave * 0.5 + 0.5);

                let cr = GREEN[0] * alpha;
                let cg = GREEN[1] * alpha;
                let cb = GREEN[2] * alpha;

                for (let i = 0; i < BLOBS.length; i++) {
                    const dx = x - bx[i];
                    const dy = y - by[i];

                    const dd = dx * dx + dy * dy;

                    if (dd < r2) {
                        const dist = Math.sqrt(dd);
                        const f = 1 - dist / BLOB_RADIUS;
                        const contrib = BLOB * f * f;
                        const col = BLOBS[i].color;

                        alpha += contrib;

                        cr += col[0] * contrib;
                        cg += col[1] * contrib;
                        cb += col[2] * contrib;

                        applyLens(
                            x,
                            y,
                            bx[i],
                            by[i],
                            dist,
                            BLOB_RADIUS,
                            BLOB_REFRACT,
                            BLOB_MAG,
                            1,
                        );
                    }
                }

                if (lens.grow > 0.001) {
                    const dx = x - lens.x;
                    const dy = y - lens.y;

                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < POINTER_RADIUS) {
                        const g = lens.grow;
                        const nd = dist / POINTER_RADIUS;

                        const contrib = POINTER * g * (1 - nd);

                        alpha += contrib;

                        cr += GREEN[0] * contrib;
                        cg += GREEN[1] * contrib;
                        cb += GREEN[2] * contrib;

                        applyLens(
                            x,
                            y,
                            lens.x,
                            lens.y,
                            dist,
                            POINTER_RADIUS,
                            POINTER_REFRACT,
                            POINTER_MAG,
                            g,
                        );
                    }
                }

                if (alpha < 0.012) continue;

                const r8 = Math.round(cr / alpha);
                const g8 = Math.round(cg / alpha);
                const b8 = Math.round(cb / alpha);

                if (alpha > 0.75) alpha = 0.75;

                ctx!.fillStyle = `rgba(${r8}, ${g8}, ${b8}, ${alpha})`;

                const ds = DOT * acc.mag;
                const off = (ds - DOT) / 2;
                ctx!.fillRect(x + acc.dx - off, y + acc.dy - off, ds, ds);
            }
        }
    }

    function drawStatic() {
        const w = window.innerWidth;
        const h = window.innerHeight;

        ctx!.clearRect(0, 0, w, h);

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                ctx!.fillStyle = `rgba(${GREEN[0]}, ${GREEN[1]}, ${GREEN[2]}, ${BASE})`;
                ctx!.fillRect(c * CELL, r * CELL, DOT, DOT);
            }
        }
    }

    let raf = 0;
    function loop(time: number) {
        draw(time);
        raf = requestAnimationFrame(loop);
    }

    function onResize() {
        resize();
        if (reduceMotion) drawStatic();
    }

    function onPointerMove(e: PointerEvent) {
        pointer.x = e.clientX;
        pointer.y = e.clientY;
        pointer.active = true;
    }

    function onPointerLeave() {
        pointer.active = false;
    }

    function onVisibilityChange() {
        if (document.hidden) {
            cancelAnimationFrame(raf);
            raf = 0;
        } else if (!reduceMotion && !raf) {
            raf = requestAnimationFrame(loop);
        }
    }

    window.addEventListener("resize", onResize);
    window.addEventListener("pointermove", onPointerMove, { passive: true });
    window.addEventListener("pointerleave", onPointerLeave);
    document.addEventListener("visibilitychange", onVisibilityChange);

    resize();

    if (reduceMotion) {
        drawStatic();
    } else {
        raf = requestAnimationFrame(loop);
    }

    return () => {
        cancelAnimationFrame(raf);
        window.removeEventListener("resize", onResize);
        window.removeEventListener("pointermove", onPointerMove);
        window.removeEventListener("pointerleave", onPointerLeave);
        document.removeEventListener("visibilitychange", onVisibilityChange);
    };
}
