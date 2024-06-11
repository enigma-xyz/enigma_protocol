import { Button, HStack, Heading } from "@chakra-ui/react";
import Link from "next/link";

export default function HeaderNav() {
  return (
    <HStack
      borderBottom={"1px"}
      borderBottomColor={"gray.600"}
      py={{ lg: 4, base: 3 }}
      minH={10}
      justify={"space-between"}
      px={{ lg: 4, base: 3 }}
    >
      <Heading>
        <Link href={"/"}>Enigma</Link>
      </Heading>
      <nav></nav>

      <Button
        fontWeight={600}
        size={{ md: "lg", base: "md" }}
        variant={"outline"}
      >
        Connect Wallet
      </Button>
    </HStack>
  );
}
