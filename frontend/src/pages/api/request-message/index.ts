import axios from "axios";
import { mainHandler } from "@/utils";

import { type NextApiRequest, type NextApiResponse } from "next";

const TIME = new Date();
const FUTURE = new Date(
  TIME.getFullYear(),
  TIME.getMonth(),
  TIME.getDate() + 7,
  TIME.getHours(),
  TIME.getMinutes(),
  TIME.getSeconds(),
  TIME.getMilliseconds()
);
const domain = "Enigma";
const statement = "Please sign this message to confirm your identity.";
// const uri = "https://example.com";
const expirationTime = FUTURE.toISOString();
const notBefore = TIME.toISOString();
const nonce = Math.random().toString(16).substring(2);
const timeout = 60;
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  return mainHandler(req, res, {
    POST,
  });
}
export async function POST(req: NextApiRequest, res: NextApiResponse) {
  const { address, network, chain = "solana" } = req.body;
  const API_URL =
    process.env.NEXT_PUBLIC_AUTH_API_URL ||
    "https://laughing-journey-6wvrvrgjwpp3xq7v-3800.app.github.dev";
  if (!address) throw new Error("No address provided");
  try {
    const response = await axios.post(
      `${API_URL}/auth/web3/solana/request-message`,
      {
        address,
        network,
        chain,
      }
    );
    console.log({ d: response?.data });

    res.status(200).json({ success: true, message: response?.data?.data });
  } catch (error: any) {
    console.error("Error requesting message:", error);
    res.status(500).json({ success: false, message: "Internal server error" });
  }
}
function createAuthMessage(
  address: string,
  domain: string,
  statement: string,
  timeout: number,
  expirationTime: string,
  notBefore: string,
  nonce: string
) {
  return `${statement}
    Domain: ${domain}
    Address: ${address}
    Nonce: ${nonce}
    Not before: ${notBefore}
    Expiration time: ${expirationTime}
    Timeout: ${timeout}
  `;
}
