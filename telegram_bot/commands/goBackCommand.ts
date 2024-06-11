import { MyContext } from "../bot";
import { rootMenu } from "../menus/rootMenu";

export const handleGoBackCommand = async (ctx: MyContext) => {
  const originalMessage = "Welcome to the bot! Here's what it does...";

  try {
    // Check if the message has a caption
    if (ctx.callbackQuery?.message?.caption) {
      await ctx.editMessageCaption({
        caption: originalMessage,
        reply_markup: rootMenu,
      });
    } else {
      await ctx.editMessageText(originalMessage, {
        reply_markup: rootMenu,
      });
    }
  } catch (error) {
    console.error("Error editing message:", error);
    // Handle the error or send an error message to the user
  }
};