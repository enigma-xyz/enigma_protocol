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
exports.handleWelcomeMessage = exports.handleWelcomeCommand = void 0;
const handleWelcomeCommand = (ctx) => __awaiter(void 0, void 0, void 0, function* () {
    ctx.session.currentStep = "awaitingName";
    yield ctx.reply("Hi! What's your name?");
});
exports.handleWelcomeCommand = handleWelcomeCommand;
const handleWelcomeMessage = (ctx) => __awaiter(void 0, void 0, void 0, function* () {
    var _a;
    const name = (_a = ctx.message) === null || _a === void 0 ? void 0 : _a.text;
    if (name) {
        yield ctx.reply(`Nice to meet you, ${name}!`);
        ctx.session.currentStep = "idle";
    }
    else {
        yield ctx.reply("Hi! What's your name?");
    }
});
exports.handleWelcomeMessage = handleWelcomeMessage;
