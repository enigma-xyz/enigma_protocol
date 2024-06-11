import { bot } from "./bot";
import { rootMenu } from "./menus/rootMenu";
import { handleStartCommand } from "./commands/startCommand";
import { handleWelcomeMessage } from "./commands/welcomeCommand";
import { handleBuyToken } from "./commands/buyCommand";
import { handleSellCommand } from "./commands/sellCommand";

bot.use(rootMenu);

bot.command("start", handleStartCommand);
bot.command("sell", handleSellCommand);

bot.on("message:text", async (ctx) => {
  if (ctx.session.currentStep === "awaitingName") {
    await handleWelcomeMessage(ctx);
  } else if (ctx.session.currentStep === "awaitingToken") {
    await handleBuyToken(ctx);
  }
});

bot.start();



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