import DepositBox from "@/components/DepositBox";
import HeaderNav from "@/components/HeaderNav";
import { LineDivider } from "@/components/LineDivider";
import SectionHeading from "@/components/SectionHeading";
import {
  Box,
  Flex,
  HStack,
  Heading,
  List,
  ListItem,
  ResponsiveValue,
  Stack,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
} from "@chakra-ui/react";

export default function VaultPage() {
  const walletBalance = 120;
  const tabBtnStyle = {
    fontSize: { xl: "24px", base: "16px", md: "22px" },
    border: { sm: "2px" },
    borderColor: { sm: "transparent" },
    _hover: {
      bg: "orange-rgba.100",
      color: "orange.400",
      borderColor: "orange-rgba.200",
    },
    rounded: { sm: "full", base: "md" },
    color: "gray.400",
    fontWeight: 400,
    _selected: {
      color: "white",
      bg: "orange.500",
      borderColor: "transparent",
      _hover: {
        borderColor: "transparent",
        bg: "orange-rgba.500",
        color: "white",
      },
    },
    w: { base: "full", sm: "auto" },
    flexShrink: { base: 0, sm: 1 },
    px: { lg: 6, base: 3, md: 4 },
  };
  const tabPanelStyle = {
    px: 0,
    display: "flex",
    flexWrap: { base: "wrap", lg: "nowrap" } as ResponsiveValue<
      "wrap" | "nowrap"
    >,
    w: "full",
    gap: 10,
    py: 8,
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
            Multiply your yields with delta-neutral market making strategies
            focused on SOL.
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
        <Flex mx={"auto"} w={"full"} maxW={"1300"}>
          <Tabs
            display={"flex"}
            flexDir={"column"}
            // w={"full"}
            mx={"auto"}
            colorScheme="orange"
            variant={"solid-rounded"}
            px={3}
          >
            <TabList
              maxW={"fit-content"}
              flexWrap={{ base: "wrap", sm: "nowrap" }}
              justifyContent={{ base: "center" }}
              gap={{ lg: 8, base: 4, sm: 6 }}
              border={"1px"}
              rounded={{ sm: "full", base: "md" }}
              borderColor={"gray.600"}
              pos={"relative"}
              mx={"auto"}
              mb={8}
            >
              <Tab {...tabBtnStyle}>Vault Performance</Tab>
              <Tab {...tabBtnStyle}>Your performance</Tab>
              <Tab {...tabBtnStyle}>Overview</Tab>
            </TabList>
            <TabPanels>
              <TabPanel {...tabPanelStyle}>
                <Box flex={1} minW={{ md: 500, lg: 600, base: 350 }}>
                  <SectionHeading
                    title="Performance Breakdown"
                    containerStyleProps={{ mt: 0 }}
                  />
                  <List as={Stack} gap={3}>
                    <ListItem as={HStack} justify={"space-between"}>
                      <Text
                        as={"span"}
                        color={"gray.400"}
                        fontSize={{ base: "17px", md: "18px" }}
                        textAlign={"left"}
                        fontWeight={"bold"}
                      >
                        Total Earnings (All Time)
                      </Text>
                      <Text as={"span"} textAlign={"right"} fontWeight={"bold"}>
                        $2,903,690.85
                      </Text>
                    </ListItem>
                    <ListItem as={HStack} justify={"space-between"}>
                      <Text
                        as={"span"}
                        color={"gray.400"}
                        fontSize={{ base: "17px", md: "18px" }}
                        textAlign={"left"}
                        fontWeight={"bold"}
                      >
                        Cumulative Return
                      </Text>
                      <Text as={"span"} textAlign={"right"} fontWeight={"bold"}>
                        40.65%
                      </Text>
                    </ListItem>
                    <ListItem as={HStack} justify={"space-between"}>
                      <Text
                        as={"span"}
                        color={"gray.400"}
                        fontSize={{ base: "17px", md: "18px" }}
                        textAlign={"left"}
                        fontWeight={"bold"}
                      >
                        APY
                      </Text>
                      <Text as={"span"} textAlign={"right"} fontWeight={"bold"}>
                        0.95%
                      </Text>
                    </ListItem>
                  </List>
                  <SectionHeading title="Cumulative Performance" />
                  <SectionHeading title="Vault Details" />
                </Box>
                <DepositBox walletBalance={walletBalance} />
              </TabPanel>
              <TabPanel {...tabPanelStyle}>
                <Box flex={1} minW={{ md: 500, lg: 600, base: 350 }}>
                  hello stock
                </Box>
                <DepositBox walletBalance={walletBalance} />
              </TabPanel>
              <TabPanel {...tabPanelStyle}>
                <Box flex={1} minW={{ md: 500, lg: 600, base: 350 }}>
                  overview
                </Box>
                <DepositBox walletBalance={walletBalance} />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </Flex>
      </Box>
    </>
  );
}
