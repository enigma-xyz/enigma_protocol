"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.bot = void 0;
const grammy_1 = require("grammy");
const session_1 = require("./session");
exports.bot = new grammy_1.Bot("6718845274:AAHmLDgK2Ef3zYWH3DAqlvSN9QLG7pbDYk8");
exports.bot.use((0, grammy_1.session)({ initial: session_1.initialSession }));
