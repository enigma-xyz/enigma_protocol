import { MyContext } from "../bot";

export const handleWelcomeCommand = async (ctx: MyContext) => {
  ctx.session.currentStep = "awaitingName";
  await ctx.reply("Hi! What's your name?");
};

export const handleWelcomeMessage = async (ctx: MyContext) => {
  const name = ctx.message?.text;
  if (name) {
    await ctx.reply(`Nice to meet you, ${name}!`);
    ctx.session.currentStep = "idle";
  } else {
    await ctx.reply("Hi! What's your name?");
  }
};

