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
exports.handleBuyToken = exports.handleBuyCommand = void 0;
const handleBuyCommand = (ctx) => __awaiter(void 0, void 0, void 0, function* () {
    ctx.session.currentStep = "awaitingToken";
    yield ctx.reply("Enter a token symbol or address to buy");
});
exports.handleBuyCommand = handleBuyCommand;
const handleBuyToken = (ctx) => __awaiter(void 0, void 0, void 0, function* () {
    var _a;
    const token = (_a = ctx.message) === null || _a === void 0 ? void 0 : _a.text;
    if (token) {
        ctx.session.token = token;
        yield ctx.reply(`You entered the token: ${ctx.session.token}`);
    }
    else {
        yield ctx.reply("Please enter a valid token symbol or address.");
    }
});
exports.handleBuyToken = handleBuyToken;
