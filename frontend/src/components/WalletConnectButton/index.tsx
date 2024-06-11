import { useCustomSign, useWalletAccount } from "@/hooks";
import { maskWalletAddress } from "@/utils";
import { Button } from "@chakra-ui/react";
import { useWallet } from "@solana/wallet-adapter-react";
import r, {
  WalletDisconnectButton,
  WalletMultiButton,
  useWalletModal,
} from "@solana/wallet-adapter-react-ui";
import { useCallback, useEffect } from "react";

export default function WalletConnectButton() {
  const { connect, connected, connecting, disconnect, publicKey } = useWallet();
  const wm = useWalletModal();
  const { address } = useWalletAccount();
  const { signCustomMessage, signed } = useCustomSign();
  async function handleConnect() {
    try {
      wm.setVisible(true);
    } catch (error) {}
  }
  async function handleDisconnect() {
    try {
      await disconnect();
    } catch (error) {}
  }
  const signMessageCb = useCallback(signCustomMessage, [signCustomMessage]);
  useEffect(() => {
    connected && !signed && signMessageCb();
  }, [connected, signMessageCb, signed]);
  return (
    <>
      {connected ? (
        <Button onClick={async () => await handleDisconnect()}>
          {" "}
          disconnect
        </Button>
      ) : (
        <Button
          fontWeight={600}
          size={{ md: "lg", base: "md" }}
          onClick={async () => await handleConnect()}
          variant={"outline"}
        >
          Connect Wallet
        </Button>
      )}
      {connected && publicKey && <Button>{maskWalletAddress(address!)}</Button>}
    </>
  );
}
