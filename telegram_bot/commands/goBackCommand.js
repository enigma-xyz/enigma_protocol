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
exports.handleGoBackCommand = void 0;
const rootMenu_1 = require("../menus/rootMenu");
const handleGoBackCommand = (ctx) => __awaiter(void 0, void 0, void 0, function* () {
    var _a, _b;
    const originalMessage = "Welcome to the bot! Here's what it does...";
    try {
        // Check if the message has a caption
        if ((_b = (_a = ctx.callbackQuery) === null || _a === void 0 ? void 0 : _a.message) === null || _b === void 0 ? void 0 : _b.caption) {
            yield ctx.editMessageCaption({
                caption: originalMessage,
                reply_markup: rootMenu_1.rootMenu,
            });
        }
        else {
            yield ctx.editMessageText(originalMessage, {
                reply_markup: rootMenu_1.rootMenu,
            });
        }
    }
    catch (error) {
        console.error("Error editing message:", error);
        // Handle the error or send an error message to the user
    }
});
exports.handleGoBackCommand = handleGoBackCommand;
