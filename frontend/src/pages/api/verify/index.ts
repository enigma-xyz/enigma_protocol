import { mainHandler } from "@/utils";
import { PublicKey } from "@solana/web3.js";
import axios from "axios";
import base58 from "bs58";
import { type NextApiRequest, type NextApiResponse } from "next";
import nacl from "tweetnacl";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  return mainHandler(req, res, {
    POST,
  });
}
export async function POST(req: NextApiRequest, res: NextApiResponse) {
  try {
    const appId = process.env.NEXT_PUBLIC_APP_ID || "460760966854877184";
    const { message, signature, address, network, chain } = req.body;
    const API_URL =
      process.env.NEXT_PUBLIC_AUTH_API_URL ||
      "https://laughing-journey-6wvrvrgjwpp3xq7v-3800.app.github.dev";
    const response = await axios.post(
      `${API_URL}/auth/web3/solana/verify`,
      {
        message,
        signature,
        address,
        network,
        chain,
      },
      {
        headers: {
          "x-app-id": appId,
        },
      }
    );

    res.status(200).json({ success: true, token: response?.data?.data });
  } catch (error: any) {
    console.error("Error verifying message:", error);
    res.status(500).json({
      success: false,
      message: error?.response?.statusText || "Something went wrong",
    });
  }
}
