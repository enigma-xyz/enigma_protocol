"use strict";
// import { Menu } from "@grammyjs/menu";
// import { MyContext } from "../bot";
Object.defineProperty(exports, "__esModule", { value: true });
exports.sellMenu = void 0;
// export const sellMenu = new Menu<MyContext>("sell-menu")
//   .back("Go Back")
//   .text("Refresh", (ctx) => ctx.reply("You clicked refresh"));
const menu_1 = require("@grammyjs/menu");
const goBackCommand_1 = require("../commands/goBackCommand");
exports.sellMenu = new menu_1.Menu("sell-menu")
    .text("Go Back", goBackCommand_1.handleGoBackCommand)
    .text("Refresh", (ctx) => ctx.reply("You clicked refresh"));
