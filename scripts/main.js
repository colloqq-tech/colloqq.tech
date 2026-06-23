import { setCurrentYear } from "./temp/year.js";
import { initZoomGuard } from "./temp/zoom-guard.js";
import { initBackground } from "./temp/background.js";

setCurrentYear();
initZoomGuard();
initBackground(document.getElementById("bg"));
