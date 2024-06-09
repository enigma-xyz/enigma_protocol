import {
  Box,
  Button,
  FormControl,
  FormLabel,
  HStack,
  Input,
  Stack,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
} from "@chakra-ui/react";
import { useFormik } from "formik";
export default function DepositBox() {
  const formik = useFormik({
    initialValues: {
      amount: "",
    },
    onSubmit: (values) => {
      alert(JSON.stringify(values, null, 2));
    },
  });
  const { values, handleChange, handleSubmit } = formik;
  return (
    <Box>
      <Tabs>
        <TabList>
          <Tab>Deposit</Tab>
          <Tab>Withdraw</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <Stack
              as="form"
              justifyContent={"space-between"}
              // @ts-ignore
              onSubmit={handleSubmit}
            >
              <Stack>
                <FormControl>
                  <FormLabel>Deposit amount:</FormLabel>
                  <Input
                    type="text"
                    name="amount"
                    value={values.amount}
                    onChange={handleChange}
                  />
                </FormControl>
                <HStack>
                  <Button>25%</Button>
                  <Button>50%</Button>
                  <Button>75%</Button>
                  <Button>MAX</Button>
                </HStack>
              </Stack>
              <Button type="submit" size={"lg"}>
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
