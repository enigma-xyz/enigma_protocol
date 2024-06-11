import { Bot, Context, InputFile, session, SessionFlavor } from "grammy";
import { MySession, initialSession } from "./session";

export type MyContext = Context & SessionFlavor<MySession>;

export const bot = new Bot<MyContext>("6718845274:AAHmLDgK2Ef3zYWH3DAqlvSN9QLG7pbDYk8");

bot.use(session({ initial: initialSession }));