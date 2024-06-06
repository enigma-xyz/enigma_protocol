import HeaderNav from "@/components/HeaderNav";
import VaultCard from "@/components/HeaderNav/VaultCard";
import { Button, Flex, Stack } from "@chakra-ui/react";

export default function Home() {
  return (
    <>
      <HeaderNav />
      <main>
        <Flex gap={5} wrap={"wrap"} py={8} px={5} align={"center"}>
          <VaultCard />
          <VaultCard />
        </Flex>
      </main>
    </>
  );
}
