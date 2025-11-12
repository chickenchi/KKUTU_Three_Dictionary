// atoms.ts
import { atom } from "recoil";

export const modalState = atom({
  key: "modalState",
  default: false,
});

export const optionState = atom<string>({
  key: "optionState",
  default: "villain",
});

export const subjectState = atom({
  key: "subjectState",
  default: "주제 없음",
});

export const wordValueState = atom<string>({
  key: "wordValueState",
  default: "",
});

export const practiceOptionOpenSetting = atom<boolean>({
  key: "practiceOptionOpenSetting",
  default: false,
});

export const shMisTypeState = atom<string>({
  key: "shMisTypeState",
  default: "length",
});

export const settingOptionState = atom<string>({
  key: "settingOptionState",
  default: "mission",
});

export const serverOptionState = atom<string>({
  key: "serverOptionState",
  default: "kkuko",
});
