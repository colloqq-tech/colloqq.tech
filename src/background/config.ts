export type RGB = readonly [number, number, number];

export const GREEN: RGB = [133, 203, 51];
export const PINK: RGB = [231, 90, 124];

export const CELL = 8;
export const DOT = 2;
export const BASE = 0.05;
export const WAVE = 0.5;

export const BLOB = 0.55;
export const BLOB_RADIUS = 400;

export const BLOB_MAG = 1;
export const BLOB_REFRACT = 0.6;

export const POINTER = 0.25;
export const POINTER_RADIUS = 400;

export const POINTER_MAG = 2;
export const POINTER_REFRACT = 0.6;

export const POINTER_FOLLOW = 6;
export const POINTER_GROW = 4;

export interface Blob {
    fx: number;
    fy: number;
    px: number;
    py: number;
    ax: number;
    ay: number;
    color: RGB;
}

export const BLOBS: Blob[] = [
    { fx: 0.31, fy: 0.23, px: 0.0, py: 1.3, ax: 0.42, ay: 0.4, color: GREEN },
    { fx: 0.24, fy: 0.34, px: 2.1, py: 0.4, ax: 0.4, ay: 0.42, color: PINK },
    { fx: 0.38, fy: 0.27, px: 4.0, py: 3.1, ax: 0.38, ay: 0.4, color: GREEN },
    { fx: 0.24, fy: 0.34, px: 5.24, py: 3.54, ax: 0.4, ay: 0.42, color: PINK },
];
