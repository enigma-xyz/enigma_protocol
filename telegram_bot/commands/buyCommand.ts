import { MyContext } from "../bot";

export const handleBuyCommand = async (ctx: MyContext) => {
  ctx.session.currentStep = "awaitingToken";
  await ctx.reply("Enter a token symbol or address to buy");
};

export const handleBuyToken = async (ctx: MyContext) => {
  const token = ctx.message?.text;
  if (token) {
    ctx.session.token = token;
    await ctx.reply(`You entered the token: ${ctx.session.token}`);
  } else {
    await ctx.reply("Please enter a valid token symbol or address.");
  }
};