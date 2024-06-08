import HeaderNav from "@/components/HeaderNav";
import { LineDivider } from "@/components/LineDivider";
import {
  Box,
  Divider,
  Flex,
  HStack,
  Heading,
  Stack,
  Tab,
  TabIndicator,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
} from "@chakra-ui/react";

export default function VaultPage() {
  const tabBtnStyle = {
    fontSize: { lg: "24px", base: "16px", md: "22px" },
    border: { sm: "2px" },
    borderColor: { sm: "transparent" },
    _hover: {
      bg: "orange-rgba.100",
      color: "orange.400",
      borderColor: "orange-rgba.200",
    },
    rounded: { sm: "full", base: "md" },
    color: "gray.400",
    _selected: {
      fontWeight: 600,
      color: "white",
      bg: "orange-rgba.600",
      borderColor: "transparent",
      _hover: {
        borderColor: "transparent",
        bg: "orange-rgba.600",
        color: "white",
      },
    },
    w: { base: "full", sm: "auto" },
    flexShrink: { base: 0, sm: 1 },
    px: { lg: 6, base: 3, md: 4 },
  };
  return (
    <>
      <HeaderNav />
      <Box as="main" mx={"auto"} maxW={"1350"}>
        <Box
          textAlign={"center"}
          py={{ lg: 12, base: 8 }}
          px={4}
          mt={10}
          bg={"#000b url('/images/pattern.jpg') center / cover no-repeat"}
          backgroundBlendMode={"darken"}
        >
          <Heading size={{ sm: "3xl", base: "2xl" }} mb={4}>
            SuperCharger
          </Heading>
          <Text fontSize={{ sm: "22px", base: "20px" }} color={"gray.300"}>
            multiply your yields with delta-neutral market making strategies
            focused on SOL
          </Text>
        </Box>
        <HStack
          wrap={{ base: "wrap", sm: "nowrap" }}
          gap={{ lg: 10, base: 5, md: 8 }}
          justify={"center"}
          px={4}
          py={10}
        >
          <Stack align={"center"}>
            <Text
              as={"span"}
              fontFamily={"var(--font-comfortaa)"}
              fontWeight={600}
              fontSize={{ md: "35px", sm: "30px", base: "28px" }}
            >
              $25,865,348.01
            </Text>
            <Text as={"span"} color={"gray.300"} fontSize={"17px"}>
              Total Value Locked
            </Text>
          </Stack>

          <LineDivider
            styleProps={{
              w: { base: "100%", sm: "2px", md: "3px" },
              h: { base: "2px", sm: "55px" },
              flexShrink: 0,
            }}
          />
          <Stack align={"center"}>
            <Text
              fontFamily={"var(--font-comfortaa)"}
              as={"span"}
              fontWeight={600}
              fontSize={{ md: "35px", sm: "30px", base: "28px" }}
            >
              $30,000,000.00
            </Text>
            <Text as={"span"} color={"gray.300"} fontSize={"17px"}>
              Max Capacity
            </Text>
          </Stack>
        </HStack>
        <Flex justify={"center"} maxW={1200} mx={"auto"}>
          <Tabs colorScheme="orange" variant={"solid-rounded"} px={3}>
            <TabList
              flexWrap={{ base: "wrap", sm: "nowrap" }}
              justifyContent={{ base: "center" }}
              gap={{ lg: 8, base: 4, sm: 6 }}
              border={"1px"}
              rounded={{ sm: "full", base: "md" }}
              borderColor={"gray.600"}
              pos={"relative"}
            >
              <Tab {...tabBtnStyle}>Vault Performance</Tab>
              <Tab {...tabBtnStyle}>Your performance</Tab>
              <Tab {...tabBtnStyle}>Overview</Tab>
              {/* <Box pos={"absolute"} h={"full"}>
                <TabIndicator
                  top={0}
                  height="full"
                  bg="orange.600"
                  borderRadius="full"
                  border={"2px"}
                  borderColor={"orange-rgba.200"}
                  zIndex={-1}
                />
              </Box> */}
            </TabList>
            <TabPanels>
              <TabPanel>hello value</TabPanel>
              <TabPanel>hello stock</TabPanel>
              <TabPanel>overview</TabPanel>
            </TabPanels>
          </Tabs>
        </Flex>
      </Box>
    </>
  );
}
