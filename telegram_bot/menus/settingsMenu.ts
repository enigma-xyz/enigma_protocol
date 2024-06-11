import { Menu } from "@grammyjs/menu";
import { MyContext } from "../bot";

export const settingsMenu = new Menu<MyContext>("settings-menu")
  .text("Show Credits", (ctx) => ctx.reply("Powered by grammY"))
  .back("Go Back");

