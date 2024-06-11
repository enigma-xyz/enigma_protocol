import { InlineKeyboard, InputFile } from "grammy";
import { MyContext } from "../bot";
import { rootMenu } from "../menus/rootMenu";

export const handleStartCommand = async (ctx: MyContext) => {
  if (ctx.chat?.type === "private") {
    ctx.session.currentStep = "idle";

    let message = "Welcome to the bot! Here's what it does...";

    if (ctx.session.startCount === 0) {
      const imagePath = "./public/image.png";
      const imageFile = new InputFile(imagePath);

      await ctx.replyWithPhoto(imageFile, {
        caption: message,
        reply_markup: rootMenu,
      });
    } else {
      await ctx.reply(message, {
        reply_markup: rootMenu,
      });
    }

    ctx.session.startCount++;
  } else {
    // Handle the /start command in a group chat
    await ctx.reply(
      "Hey there! I'm a bot. To interact with me, please send me a private message.",
      {
        reply_markup: new InlineKeyboard().url(
          "Start in Private Chat",
          `https://t.me/${ctx.me.username}?start`
        ),
      }
    );
  }
};
