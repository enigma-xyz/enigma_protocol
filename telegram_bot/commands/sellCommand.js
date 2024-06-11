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
exports.handleSellCommand = void 0;
const sellMenu_1 = require("../menus/sellMenu");
const handleSellCommand = (ctx) => __awaiter(void 0, void 0, void 0, function* () {
    var _a;
    const message = "You do not have any tokens yet! Start trading in the Buy menu.";
    try {
        // Check if the message is a callback query (button click)
        if (ctx.callbackQuery) {
            // Check if the message has a caption
            if ((_a = ctx.callbackQuery.message) === null || _a === void 0 ? void 0 : _a.caption) {
                yield ctx.editMessageCaption({
                    caption: message,
                    reply_markup: sellMenu_1.sellMenu,
                });
            }
            else {
                yield ctx.editMessageText(message, {
                    reply_markup: sellMenu_1.sellMenu,
                });
            }
        }
        else {
            // If it's a command, send a new message
            yield ctx.reply(message, {
                reply_markup: sellMenu_1.sellMenu,
            });
        }
    }
    catch (error) {
        console.error("Error handling sell command:", error);
        // Handle the error or send an error message to the user
    }
});
exports.handleSellCommand = handleSellCommand;
