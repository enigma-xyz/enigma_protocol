import { chakraTheme } from "@/constants/theme";
import { ColorModeScript } from "@chakra-ui/react";
import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en">
      <Head />
      <body>
        <Main />

        <ColorModeScript
          initialColorMode={chakraTheme.config.initialColorMode}
        />
        <NextScript />
      </body>
    </Html>
  );
}
