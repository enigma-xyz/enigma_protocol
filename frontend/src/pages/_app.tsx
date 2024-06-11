import { chakraTheme } from "@/constants/theme";
import { fonts } from "@/lib/fonts";
import "@/styles/globals.css";
import { ChakraProvider } from "@chakra-ui/react";
import type { AppProps } from "next/app";
import React, { useMemo } from "react";
import {
  ConnectionProvider,
  WalletProvider,
} from "@solana/wallet-adapter-react";
import { WalletModalProvider } from "@solana/wallet-adapter-react-ui";
import { clusterApiUrl } from "@solana/web3.js";

import "@solana/wallet-adapter-react-ui/styles.css";

export default function App({ Component, pageProps }: AppProps) {
  const network = clusterApiUrl("mainnet-beta");

  const wallets = useMemo(() => [], []);

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
      <ConnectionProvider endpoint={network}>
        <WalletProvider wallets={wallets} autoConnect>
          <WalletModalProvider>
            <ChakraProvider theme={chakraTheme}>
              <Component {...pageProps} />
            </ChakraProvider>
          </WalletModalProvider>
        </WalletProvider>
      </ConnectionProvider>
    </>
  );
}
