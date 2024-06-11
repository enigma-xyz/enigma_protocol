import { Menu } from "@grammyjs/menu";
import { MyContext } from "../bot";
import { handleWelcomeCommand } from "../commands/welcomeCommand";
import { handleBuyCommand } from "../commands/buyCommand";
import { sellMenu } from "./sellMenu";
import { settingsMenu } from "./settingsMenu";
import { handleSellCommand } from "../commands/sellCommand";

export const rootMenu = new Menu<MyContext>("root-menu")
  .text("Welcome", handleWelcomeCommand)
  .row()
  .text("Buy", handleBuyCommand)
  .text("Sell", handleSellCommand)
  .row()
  .submenu("Positions", "settings-menu")
  .submenu("Limit Orders", "settings-menu")
  .submenu("DCA Orders", "settings-menu")
  .row()
  .submenu("Copy Trade", "settings-menu")
  .submenu("LP Snipper", "settings-menu")
  .row()
  .submenu("New Pairs", "settings-menu")
  .submenu("Referrals", "settings-menu")
  .submenu("Settings", "settings-menu")
  .row()
  .submenu("Bridge", "settings-menu")
  .submenu("Withdraw", "settings-menu")
  .row()
  .submenu("Help", "settings-menu")
  .submenu("Refresh", "settings-menu")
  .row();

rootMenu.register(settingsMenu);
rootMenu.register(sellMenu);