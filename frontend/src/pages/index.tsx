import HeaderNav from "@/components/HeaderNav";
import VaultCard from "@/components/VaultCard";
import { Button, Flex, Stack } from "@chakra-ui/react";

export default function Home() {
  return (
    <>
      <HeaderNav />
      <main>
        <Flex gap={5} wrap={"wrap"} py={8} px={4} justify={"center"}>
          <VaultCard />
          <VaultCard />
        </Flex>
      </main>
    </>
  );
}
