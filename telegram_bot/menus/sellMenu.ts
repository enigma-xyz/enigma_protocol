// import { Menu } from "@grammyjs/menu";
// import { MyContext } from "../bot";

// export const sellMenu = new Menu<MyContext>("sell-menu")
//   .back("Go Back")
//   .text("Refresh", (ctx) => ctx.reply("You clicked refresh"));

import { Menu } from "@grammyjs/menu";
import { MyContext } from "../bot";
import { handleGoBackCommand } from "../commands/goBackCommand";

export const sellMenu = new Menu<MyContext>("sell-menu")
  .text("Go Back", handleGoBackCommand)
  .text("Refresh", (ctx) => ctx.reply("You clicked refresh"));
