import { Comfortaa, Red_Hat_Display } from "next/font/google";

const comfortaa = Comfortaa({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-comfortaa",
});
const redHatDisplay = Red_Hat_Display({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-redhat",
});

export const fonts = {
  comfortaa,
  redHatDisplay,
};
