import {
  Box,
  Button,
  Divider,
  HStack,
  Heading,
  Image,
  LinkBox,
  LinkOverlay,
  Stack,
  Text,
  VStack,
} from "@chakra-ui/react";
import { Link } from "@chakra-ui/next-js";
import { LineDivider } from "../LineDivider";
export default function VaultCard() {
  return (
    <LinkBox
      display={"flex"}
      flexDir={"column"}
      rounded={"14px"}
      w={"full"}
      maxW={{ base: 450, lg: 500 }}
      border={"1px"}
      borderColor={"gray.600"}
      _hover={{
        borderColor: "orange.400",
      }}
      id="vault"
      className="link-box"
      overflow={"hidden"}
    >
      <Box minH={"150"} maxH={"250"}>
        <LinkOverlay href="/vault/supercharge">
          <Image src="/images/pattern.jpg" w={"full"} maxH={"full"} alt="" />
        </LinkOverlay>
      </Box>
      <Box py={3} bg={"blackAlpha.600"} sx={{ backdropFilter: "blur(10px)" }}>
        <Heading textAlign={"center"} fontWeight={700}>
          <LinkOverlay href="/vault/supercharge">SuperCharger</LinkOverlay>
        </Heading>
        <HStack
          mt={2}
          mb={4}
          h={"25px"}
          divider={<Divider orientation="vertical" />}
          justify={"center"}
        >
          <HStack>
            <Text as={"span"} fontWeight={600}>
              Deposit:
            </Text>
          </HStack>
          <HStack>
            <Text as={"span"} fontWeight={600}>
              Trading:
            </Text>
          </HStack>
        </HStack>
        <HStack
          sx={{
            ".link-box:hover &": {
              translateY: "-10px",
            },
          }}
          transform={"auto"}
          transition={"0.3s ease-out"}
          h={"80px"}
          justify={"space-around"}
          mb={2}
          mt={4}
          borderY={"1px"}
          borderColor={"gray.300"}
          py={3}
          divider={<LineDivider styleProps={{ w: "2px" }} />}
        >
          <VStack>
            <Text as={"span"}>APY </Text>
            <Text as={"span"} fontSize={"20px"} fontWeight={600}>
              41.24%
            </Text>
          </VStack>
          <VStack>
            <Text as={"span"}>TVL</Text>
            <Text as={"span"} fontSize={"20px"} fontWeight={600}>
              $25.9M
            </Text>
          </VStack>
          <VStack>
            <Text as={"span"}>Capacity</Text>
            <Text as={"span"} fontSize={"20px"} fontWeight={600}>
              86.48%
            </Text>
          </VStack>
        </HStack>
        <Box
          overflow={"hidden"}
          sx={{
            ".link-box:hover &": {
              h: "auto",
            },
          }}
        >
          <Box
            p={4}
            pb={"2px"}
            sx={{
              ".link-box:hover &": {
                translateY: "0",
              },
            }}
            transition={"0.3s ease-out"}
            transform={"auto"}
            translateY={"60px"}
          >
            <Button
              w={"full"}
              as={Link}
              href="/vault/supercharge"
              textDecor="none!important"
            >
              Open Vault
            </Button>
          </Box>
        </Box>
      </Box>
    </LinkBox>
  );
}
