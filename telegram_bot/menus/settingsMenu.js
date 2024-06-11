"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.settingsMenu = void 0;
const menu_1 = require("@grammyjs/menu");
exports.settingsMenu = new menu_1.Menu("settings-menu")
    .text("Show Credits", (ctx) => ctx.reply("Powered by grammY"))
    .back("Go Back");
