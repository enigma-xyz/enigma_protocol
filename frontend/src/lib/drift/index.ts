import { Connection } from "@solana/web3.js";
import { DriftClient, Wallet, loadKeypair } from "@drift-labs/sdk";
import {
  clusterApiUrl,
  Keypair,
  LAMPORTS_PER_SOL,
  PublicKey,
  SystemProgram,
  Transaction,
} from "@solana/web3.js";

import { Magic } from "magic-sdk";

import { SolanaExtension } from "@magic-ext/solana";

const connection = new Connection(clusterApiUrl("devnet"));

const magic = new Magic("pk_live_5936487971702267", {
  extensions: [
    new SolanaExtension({
      rpcUrl: "SOLANA_RPC_NODE_URL",
    }),
  ],
});

magic.user.getMetadata();
async function getUserPublicKey() {
  const metadata = await magic.user.getMetadata();
  const publicKey = metadata.publicAddress!;
  const userPublicKey = new PublicKey(metadata.publicAddress);

  return publicKey;
}

async function connectWallet() {
  const publicKey = await getUserPublicKey();

  const wallet = new Wallet(publicKey);
  return wallet;
}

export const driftClient = new DriftClient({
  connection,
  wallet: magic.wallet,
  env: "mainnet-beta",
});
