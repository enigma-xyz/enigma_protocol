import { type NextApiRequest, type NextApiResponse } from "next";
import axios from "axios";
export async function apiPost<T = any>(
  endpoint: string,
  params: Record<string, any>
): Promise<T> {
  const result = await axios.post(`${endpoint}`, params, {
    headers: {
      "content-type": "application/json",
    },
  });
  return result.data;
}
export function maskWalletAddress(
  walletAddress: string,
  visibleChars: number = 5
): string {
  if (!walletAddress || walletAddress.length < visibleChars * 2) {
    return walletAddress;
  }

  const visiblePart = walletAddress.slice(0, visibleChars);
  const hiddenPart = "...";
  const lastVisiblePart = walletAddress.slice(-visibleChars);

  return `${visiblePart}${hiddenPart}${lastVisiblePart}`;
}

export type HTTP_METHOD = "GET" | "PUT" | "POST" | "DELETE";
export type HTTP_METHOD_CB = (
  req: NextApiRequest,
  res: NextApiResponse
) => Promise<void>;
export async function mainHandler(
  req: NextApiRequest,
  res: NextApiResponse,
  {
    GET,
    PUT,
    POST,
    DELETE,
  }: {
    GET?: HTTP_METHOD_CB;
    POST?: HTTP_METHOD_CB;
    PUT?: HTTP_METHOD_CB;
    DELETE?: HTTP_METHOD_CB;
  }
) {
  const method = req.method as HTTP_METHOD;
  switch (method) {
    case "GET":
      return await GET?.(req, res);
    case "POST":
      return await POST?.(req, res);
    case "PUT":
      return PUT?.(req, res);
    case "DELETE":
      return DELETE?.(req, res);

    default:
      return res.status(405).end();
  }
}
