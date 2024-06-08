import { Box } from "@chakra-ui/react";

export const LineDivider = ({
  styleProps,
}: {
  styleProps?: Record<string, any>;
}) => {
  return (
    <Box
      h={"50px"}
      w={"1"}
      rounded={"full"}
      bg={"gray.600"}
      {...styleProps}
    ></Box>
  );
};
