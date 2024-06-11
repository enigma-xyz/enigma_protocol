export interface MySession {
  currentStep: "idle" | "awaitingToken" | "awaitingName";
  token: string;
  startCount: number;
  selectedMenu: string;
}

export const initialSession = (): MySession => ({
  currentStep: "idle",
  token: "",
  startCount: 0,
  selectedMenu: "",
});
