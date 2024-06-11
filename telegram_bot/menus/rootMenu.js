"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.rootMenu = void 0;
const menu_1 = require("@grammyjs/menu");
const welcomeCommand_1 = require("../commands/welcomeCommand");
const buyCommand_1 = require("../commands/buyCommand");
const sellMenu_1 = require("./sellMenu");
const settingsMenu_1 = require("./settingsMenu");
const sellCommand_1 = require("../commands/sellCommand");
exports.rootMenu = new menu_1.Menu("root-menu")
    .text("Welcome", welcomeCommand_1.handleWelcomeCommand)
    .row()
    .text("Buy", buyCommand_1.handleBuyCommand)
    .text("Sell", sellCommand_1.handleSellCommand)
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
exports.rootMenu.register(settingsMenu_1.settingsMenu);
exports.rootMenu.register(sellMenu_1.sellMenu);
