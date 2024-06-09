import { Box, HStack, useRadio, useRadioGroup } from "@chakra-ui/react";
import { LineDivider } from "../LineDivider";
import { useCallback, useEffect, useMemo, useState } from "react";

function RadioCard(props: Record<string, any>) {
  const { getInputProps, getRadioProps } = useRadio(props);

  const input = getInputProps();
  const checkbox = getRadioProps();

  const radioBtnStyle = {
    variant: "outline",
    border: "none",
    ...{ ...(props?.isFirst && { roundedLeft: "full" }) },
    ...{ ...(props?.isLast && { roundedRight: "full" }) },
    fontWeight: 500,
    color: "orange.200",
    _hover: {
      color: "white",
      bg: "orange.500",
      borderColor: "orange-rgba.200",
    },
  };
  return (
    <Box as="label">
      <input {...input} />
      <Box
        {...checkbox}
        {...radioBtnStyle}
        cursor="pointer"
        _checked={{
          bg: "orange.500",
          color: "white",
        }}
        _focus={{
          bg: "orange.500",
        }}
        px={4}
        py={2}
      >
        {props.children}
      </Box>
    </Box>
  );
}

export function CustomRadioGroup({
  onChange,
  initialValue = 0,
  totalAmount = 0,
}: {
  onChange?: (value: string) => void;
  initialValue?: number;
  totalAmount?: number;
}) {
  const [defaultSelectedValue, setDefaultSelectedValue] = useState("");
  const options = useMemo(() => ["25", "50", "75", "100"], []);

  function getMatchingPercentage() {
    if (totalAmount === 0 || initialValue === 0) {
      return "";
    }

    const percents = options;
    const calculatedPercent = (initialValue / totalAmount) * 100;

    const matchedPercent = percents.find(
      (percent) =>
        parseFloat(percent) === parseFloat(calculatedPercent.toFixed(0))
    );

    return matchedPercent || "";
  }

  const { getRootProps, getRadioProps } = useRadioGroup({
    value: defaultSelectedValue,
    name: "deposit-percent",
    defaultValue: defaultSelectedValue,
    onChange: (value) => {
      setDefaultSelectedValue(value);
      onChange?.(value);
    },
  });

  const group = getRootProps();

  const getMatchingPercentageCb = useCallback(getMatchingPercentage, [
    initialValue,
    totalAmount,
    options,
  ]);
  useEffect(() => {
    setDefaultSelectedValue(getMatchingPercentageCb());
  }, [initialValue, getMatchingPercentageCb, defaultSelectedValue]);
  return (
    <HStack
      mt={2}
      border={"1px"}
      borderColor={"gray.600"}
      rounded={"full"}
      maxW={"max-content"}
      divider={
        <LineDivider styleProps={{ h: "40px", rounded: "none", w: "1px" }} />
      }
      {...group}
    >
      {options.map((value, index) => {
        const radio = getRadioProps({ value });
        return (
          <RadioCard
            key={value}
            index={index}
            isFirst={index === 0}
            isLast={index === options.length - 1}
            {...radio}
          >
            {value === "100" ? "MAX" : `${value}%`}
          </RadioCard>
        );
      })}
    </HStack>
  );
}
