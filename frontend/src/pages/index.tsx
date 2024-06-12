import HeaderNav from "@/components/HeaderNav";
import VaultCard, { Vault } from "@/components/VaultCard";
import { Button, Flex, Stack } from "@chakra-ui/react";
import { GetServerSidePropsContext, InferGetServerSidePropsType } from "next";

export default function Home({
  vaults,
}: InferGetServerSidePropsType<typeof getServerSideProps>) {
  console.log(vaults);
  return (
    <>
      <HeaderNav />
      <main>
        <Flex gap={5} wrap={"wrap"} py={8} px={4} justify={"center"}>
          {vaults &&
            vaults.length > 0 &&
            vaults?.map((vault, i) => (
              <VaultCard vault={vault} key={"vault" + i} />
            ))}
        </Flex>
      </main>
    </>
  );
}

export const getServerSideProps = (ctx: GetServerSidePropsContext) => {
  const vaults: Vault[] = [
    {
      name: "Drifting Tiger",
      slug: "drifting-tiger",
      cover: "/images/pattern.jpg",
      depositTokens: [
        {
          name: "USDC",
          image: "/icons/usdc.svg",
        },
      ],
      tradingTokens: [
        {
          name: "BTC",
          image: "/icons/btc.svg",
        },
        {
          name: "SOL",
          image: "/icons/sol.svg",
        },
        {
          name: "WETH",
          image: "/icons/weth.svg",
        },
        {
          name: "JUP",
          image: "/icons/jup.svg",
        },
      ],
      apy: "41.24%",
      tvl: "$25.9M",
      capacity: "86.48%",
    },
    {
      name: "Bonking Dragon",
      slug: "bonking-dragon",
      cover: "/images/pattern.jpg",
      depositTokens: [
        {
          name: "USDC",
          image: "/icons/usdc.svg",
        },
      ],
      tradingTokens: [
        {
          name: "SOL",
          image: "/icons/sol.svg",
        },
      ],
      apy: "32.40%",
      tvl: "$15.2M",
      capacity: "73.21%",
    },
    {
      name: "Double Boost",
      slug: "double-boost",
      cover: "/images/pattern.jpg",
      depositTokens: [
        {
          name: "JITOSOL",
          image: "/icons/jitosol.svg",
        },
      ],
      tradingTokens: [
        {
          name: "JITOSOL",
          image: "/icons/jitosol.svg",
        },
      ],
      apy: "21.33%",
      tvl: "$10.3M",
      capacity: "46.53%",
    },
    {
      name: "Perp Turbo",
      slug: "perp-turbo",
      cover: "/images/pattern.jpg",
      depositTokens: [
        {
          name: "USDC",
          image: "/icons/usdc.svg",
        },
      ],
      tradingTokens: [
        {
          name: "WETH",
          image: "/icons/weth.svg",
        },
        {
          name: "BTC",
          image: "/icons/btc.svg",
        },
      ],
      apy: "51.23%",
      tvl: "$35.4M",
      capacity: "89.25%",
    },
  ];
  return {
    props: {
      vaults,
    },
  };
};
