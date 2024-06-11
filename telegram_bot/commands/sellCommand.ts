import { MyContext } from "../bot";
import { sellMenu } from "../menus/sellMenu";

export const handleSellCommand = async (ctx: MyContext) => {
  const message = "You do not have any tokens yet! Start trading in the Buy menu.";

  try {
    // Check if the message is a callback query (button click)
    if (ctx.callbackQuery) {
      // Check if the message has a caption
      if (ctx.callbackQuery.message?.caption) {
        await ctx.editMessageCaption({
          caption: message,
          reply_markup: sellMenu,
        });
      } else {
        await ctx.editMessageText(message, {
          reply_markup: sellMenu,
        });
      }
    } else {
      // If it's a command, send a new message
      await ctx.reply(message, {
        reply_markup: sellMenu,
      });
    }
  } catch (error) {
    console.error("Error handling sell command:", error);
    // Handle the error or send an error message to the user
  }
};