import {
  StyleFunctionProps,
  background,
  color,
  extendTheme,
} from "@chakra-ui/react";

const config = {
  initialColorMode: "dark",
  useSystemColorMode: false,
};

export const chakraTheme = extendTheme({
  fonts: {
    heading: "var(--font-comfortaa)",
    body: "var(--font-redhat)",
    a: "var(--font-redhat)",
  },
  styles: {
    global: {
      "html, body": {
        // background: "#0B0C10",
      },
      a: {},
    },
  },
  colors: {
    orange: {
      50: "#ffe8db",
      100: "#ffc5ae",
      200: "#ffa57e",
      300: "#ff894c",
      400: "#ff6e1a",
      500: "#e65d00",
      600: "#b43c00",
      700: "#812200",
      800: "#4f0e00",
      900: "#200002",
    },
  },

  config,
  components: {
    Button: {
      variants: {
        solid: (styleProps: StyleFunctionProps) => {
          if (styleProps.colorScheme === "orange") {
            return {
              bg: "orange.500",
              color: "white",
              _hover: {
                bg: "orange.700",
              },
            };
          }
        },
        outline: (styleProps: StyleFunctionProps) => {
          if (styleProps.colorScheme === "orange") {
            return {
              _hover: {
                color: "white",
                bg: "orange.500",
                borderColor: "transparent",
              },
            };
          }
        },
      },
      baseStyle: {
        rounded: "full",
      },
      defaultProps: {
        colorScheme: "orange",
        variant: "solid",
      },
    },
  },
});
