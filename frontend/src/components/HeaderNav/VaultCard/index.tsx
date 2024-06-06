import { Box, Image, LinkBox } from "@chakra-ui/react";

export default function VaultCard() {
  return (
    <LinkBox
      rounded={"14px"}
      w={"full"}
      maxW={500}
      border={"1px"}
      borderColor={"gray.600"}
      cursor={"pointer"}
      _hover={{
        borderColor: "orange.400",
      }}
    >
      <Box minH={"200"} maxH={"250"}>
        <Image src="" alt="" />
      </Box>
    </LinkBox>
  );
}
