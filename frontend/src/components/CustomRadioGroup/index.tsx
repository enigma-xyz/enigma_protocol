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

interface CustomRadioGroupProps {
  onChange?: (value: string) => void;
  initialValue?: number;
  totalAmount?: number;
  options: string[];
  getLabel?: (value: string) => string;
  defaultValue?: string;
}

export function CustomRadioGroup({
  onChange,
  defaultValue,
  initialValue,
  totalAmount,
  options,
  getLabel = (value) => value, // Default label function just returns the value
}: CustomRadioGroupProps) {
  const [defaultSelectedValue, setDefaultSelectedValue] = useState("");

  const calculateMatchingPercentage = useCallback(() => {
    if (initialValue === undefined || totalAmount === undefined) {
      return "";
    }

    if (totalAmount === 0 || initialValue === 0) {
      return "";
    }

    const calculatedPercent = (initialValue / totalAmount) * 100;

    const matchedPercent = options.find(
      (option) =>
        parseFloat(option) === parseFloat(calculatedPercent.toFixed(0))
    );

    return matchedPercent || "";
  }, [initialValue, totalAmount, options]);

  useEffect(() => {
    if (defaultValue !== "") {
      setDefaultSelectedValue(defaultValue!);
    }
    if (initialValue !== undefined && totalAmount !== undefined) {
      setDefaultSelectedValue(calculateMatchingPercentage());
    }
  }, [initialValue, calculateMatchingPercentage, totalAmount, defaultValue]);

  const { getRootProps, getRadioProps } = useRadioGroup({
    value: defaultSelectedValue,
    name: "custom-radio-group",
    defaultValue: defaultSelectedValue,
    onChange: (value) => {
      setDefaultSelectedValue(value);
      onChange?.(value);
    },
  });

  const group = getRootProps();

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
            {getLabel(value)}
          </RadioCard>
        );
      })}
    </HStack>
  );
}
