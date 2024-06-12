import HeaderNav from "@/components/HeaderNav";
import VaultCard, { Vault } from "@/components/VaultCard";
import { Box, Button, Flex, Heading, Stack, Text } from "@chakra-ui/react";
import { GetServerSidePropsContext, InferGetServerSidePropsType } from "next";

export default function Home({
  vaults,
}: InferGetServerSidePropsType<typeof getServerSideProps>) {
  console.log(vaults);
  return (
    <>
      <HeaderNav />
      <main>
        <Box
          mx={"auto"}
          py={8}
          my={6}
          textAlign={"center"}
          maxW={1200}
          bg={"gray.900"}
        >
          <Heading mb={3} size={"4xl"}>
            Vaults
          </Heading>
          <Text fontSize={{ lg: "22px", base: "20px" }} maxW={1000} mx={"auto"}>
            Boost your trading profits through delta-neutral market making and
            liquidity provision strategies. These techniques allow you to earn
            from bid-ask spreads while maintaining hedged, market-neutral
            positions.{" "}
          </Text>
        </Box>
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
      mentions: {
        bonk: "https://cdn.prod.website-files.com/6629bf6a5421f2bbaa5e6255/662ddf0cdaeba3a5741d424c_bonkhead2.svg",
      },
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
