import { mainHandler } from "@/utils";

import { type NextApiRequest, type NextApiResponse } from "next";

const domain = "Enigma";
const statement = "Please sign this message to confirm your identity.";
// const uri = "https://example.com";
const expirationTime = new Date().getTime() + 3600 * 1000; // 1 hour later
const notBefore = new Date().getTime();
const nonce = Math.floor(Math.random() * 1000000);
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  return mainHandler(req, res, {
    POST,
  });
}
export async function POST(req: NextApiRequest, res: NextApiResponse) {
  const { address } = req.body;
  if (!address) throw new Error("No address provided");
  try {
    const message = createAuthMessage(
      address,
      domain,
      statement,
      expirationTime,
      notBefore,
      nonce
    );

    res.status(200).json({ success: true, message: message });
  } catch (error) {
    console.error("Error requesting message:", error);
    res.status(500).json({ success: false, message: "Internal server error" });
  }
}
function createAuthMessage(
  address: string,
  domain: string,
  statement: string,

  expirationTime: number,
  notBefore: number,
  nonce: number
) {
  return `${statement}
    Domain: ${domain}
    Address: ${address}
    Nonce: ${nonce}
    Not before: ${notBefore}
    Expiration time: ${expirationTime}
  `;
}
