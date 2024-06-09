import HeaderNav from "@/components/HeaderNav";
import { LineDivider } from "@/components/LineDivider";
import SectionHeading from "@/components/SectionHeading";
import {
  Box,
  Divider,
  Flex,
  HStack,
  Heading,
  List,
  ListItem,
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
        <Flex maxW={1200} mx={"auto"}>
          <Tabs
            mx={"auto"}
            colorScheme="orange"
            variant={"solid-rounded"}
            px={3}
          >
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
              <TabPanel px={0}>
                <SectionHeading title="Performance Breakdown" />
                <List as={Stack} gap={3}>
                  <ListItem as={Flex} justify={"space-between"}>
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
                  <ListItem as={Flex} justify={"space-between"}>
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
                  <ListItem as={Flex} justify={"space-between"}>
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
              </TabPanel>
              <TabPanel>hello stock</TabPanel>
              <TabPanel>overview</TabPanel>
            </TabPanels>
          </Tabs>
        </Flex>
      </Box>
    </>
  );
}
