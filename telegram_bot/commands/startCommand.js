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
exports.handleStartCommand = void 0;
const grammy_1 = require("grammy");
const rootMenu_1 = require("../menus/rootMenu");
const handleStartCommand = (ctx) => __awaiter(void 0, void 0, void 0, function* () {
    var _a;
    if (((_a = ctx.chat) === null || _a === void 0 ? void 0 : _a.type) === "private") {
        ctx.session.currentStep = "idle";
        let message = "Welcome to the bot! Here's what it does...";
        if (ctx.session.startCount === 0) {
            const imagePath = "./public/image.png";
            const imageFile = new grammy_1.InputFile(imagePath);
            yield ctx.replyWithPhoto(imageFile, {
                caption: message,
                reply_markup: rootMenu_1.rootMenu,
            });
        }
        else {
            yield ctx.reply(message, {
                reply_markup: rootMenu_1.rootMenu,
            });
        }
        ctx.session.startCount++;
    }
    else {
        // Handle the /start command in a group chat
        yield ctx.reply("Hey there! I'm a bot. To interact with me, please send me a private message.", {
            reply_markup: new grammy_1.InlineKeyboard().url("Start in Private Chat", `https://t.me/${ctx.me.username}?start`),
        });
    }
});
exports.handleStartCommand = handleStartCommand;
