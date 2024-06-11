import { mainHandler } from "@/utils";
import { PublicKey } from "@solana/web3.js";
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
    const { message, signature, address } = req.body;
    const publicKey = new PublicKey(address).toBytes();
    const encodedMessage = new TextEncoder().encode(message);
    const signatureUint8Array = base58.decode(signature);

    const verified = nacl.sign.detached.verify(
      encodedMessage,
      signatureUint8Array,
      publicKey
    );
    if (verified) {
      res
        .status(200)
        .json({ success: true, verified, message: "Valid signature" });
    } else {
      res
        .status(200)
        .json({ success: false, verified, message: "Invalid signature" });
    }
  } catch (error) {
    console.error("Error verifying message:", error);
    res.status(500).json({ success: false, message: "Internal server error" });
  }
}
