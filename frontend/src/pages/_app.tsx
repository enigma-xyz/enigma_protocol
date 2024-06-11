import { chakraTheme } from "@/constants/theme";
import { fonts } from "@/lib/fonts";
import "@/styles/globals.css";
import { ChakraProvider } from "@chakra-ui/react";
import type { AppProps } from "next/app";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <style jsx global>
        {`
          :root {
            --font-comfortaa: ${fonts.comfortaa.style.fontFamily};
            --font-redhat: ${fonts.redHatDisplay.style.fontFamily};
          }
        `}
      </style>
      <ChakraProvider theme={chakraTheme}>
        <Component {...pageProps} />
      </ChakraProvider>
    </>
  );
}
