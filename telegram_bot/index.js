"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const bot_1 = require("./bot");
const rootMenu_1 = require("./menus/rootMenu");
const startCommand_1 = require("./commands/startCommand");
const welcomeCommand_1 = require("./commands/welcomeCommand");
const buyCommand_1 = require("./commands/buyCommand");
const sellCommand_1 = require("./commands/sellCommand");
bot_1.bot.use(rootMenu_1.rootMenu);
bot_1.bot.command("start", startCommand_1.handleStartCommand);
bot_1.bot.command("sell", sellCommand_1.handleSellCommand);
bot_1.bot.on("message:text", (ctx) => __awaiter(void 0, void 0, void 0, function* () {
    if (ctx.session.currentStep === "awaitingName") {
        yield (0, welcomeCommand_1.handleWelcomeMessage)(ctx);
    }
    else if (ctx.session.currentStep === "awaitingToken") {
        yield (0, buyCommand_1.handleBuyToken)(ctx);
    }
}));
bot_1.bot.start();
// import { Bot } from "grammy";
// import { Menu } from "@grammyjs/menu";
// // Create a bot.
// const bot = new Bot("6718845274:AAHmLDgK2Ef3zYWH3DAqlvSN9QLG7pbDYk8");
// // Create a simple menu.
// const menu = new Menu("time")
//   .text(
//     "What's the time?",
//     (ctx) => ctx.editMessageText("It is " + new Date().toLocaleString()),
//   );
// // Make it interactive.
// bot.use(menu);
// bot.command("start", async (ctx) => {
//   // Send the menu.
//   await ctx.reply("Check out this menu:", { reply_markup: menu });
// });
// bot.start();
