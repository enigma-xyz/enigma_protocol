"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.initialSession = void 0;
const initialSession = () => ({
    currentStep: "idle",
    token: "",
    startCount: 0,
    selectedMenu: "",
});
exports.initialSession = initialSession;
