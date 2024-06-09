import {
  Box,
  Button,
  FormControl,
  FormLabel,
  HStack,
  Input,
  InputGroup,
  InputRightAddon,
  Stack,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
  useRadio,
  useRadioGroup,
} from "@chakra-ui/react";
import { useFormik } from "formik";
import { useRef, useState } from "react";
import { LineDivider } from "../LineDivider";
import { CustomRadioGroup } from "../CustomRadioGroup";
export default function DepositBox({
  walletBalance = 0,
}: {
  walletBalance?: number;
}) {
  const walletToken = "USDC";

  const [isInputFocus, setIsInputFocus] = useState(false);
  const formik = useFormik({
    initialValues: {
      amount: 30 as number | string,
    },
    onSubmit: (values) => {
      alert(JSON.stringify(values, null, 2));
    },
  });
  const { values, handleChange, handleSubmit } = formik;

  function onInputFocus() {
    setIsInputFocus(true);
  }
  function onInputBlur() {
    setIsInputFocus(false);
  }

  function handleRadioChange(value: string) {
    formik.setFieldValue("amount", (+value * walletBalance) / 100);
  }
  return (
    <Box
      flex={1}
      minW={{ base: 350, lg: 400 }}
      minH={400}
      border={"1px"}
      borderColor={"gray.600"}
      rounded={"xl"}
      // maxW={500}
      mx={"auto"}
    >
      <Tabs display={"flex"} flexDir={"column"} h={"full"} isFitted>
        <TabList>
          <Tab>Deposit</Tab>
          <Tab>Withdraw</Tab>
        </TabList>
        <TabPanels flexGrow={1}>
          <TabPanel h={"full"}>
            <Stack
              as="form"
              justifyContent={"space-between"}
              // @ts-ignore
              onSubmit={handleSubmit}
              h={"full"}
            >
              <Stack>
                <FormControl>
                  <HStack justify={"space-between"}>
                    <FormLabel>Deposit amount:</FormLabel>
                    <Text as="span" color={"gray.300"} fontSize={"15px"}>
                      Max: {walletBalance} {walletToken}
                    </Text>
                  </HStack>
                  <HStack
                    gap={4}
                    border={"1px"}
                    borderColor={isInputFocus ? "orange.500" : "gray.600"}
                    rounded={"full"}
                    px={3}
                  >
                    <Input
                      type="number"
                      h={"45px"}
                      step="0.01"
                      rounded={"none"}
                      _focus={{
                        outline: "none",
                        boxShadow: "none",
                        borderColor: "orange.500",
                      }}
                      border={"none"}
                      borderRight={"1px"}
                      placeholder={walletBalance + ".00"}
                      borderRightColor={"gray.600"}
                      name="amount"
                      onFocus={onInputFocus}
                      onBlur={onInputBlur}
                      value={values.amount}
                      onChange={handleChange}
                    />

                    <Text as={"span"}>{walletToken}</Text>
                  </HStack>
                </FormControl>
                <CustomRadioGroup
                  onChange={handleRadioChange}
                  initialValue={+formik.values.amount}
                  totalAmount={walletBalance}
                />
              </Stack>
              <Button
                type="submit"
                size={"lg"}
                isDisabled={
                  formik.values.amount === 0 || formik.values.amount === ""
                }
              >
                Deposit
              </Button>
            </Stack>
          </TabPanel>
          <TabPanel>Tab 2 content</TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
}
