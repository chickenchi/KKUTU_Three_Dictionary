import { atom } from "recoil";

export const answerCheckState = atom({
  key: "answerCheckState",
  default: false,
});

export const onTierCheckState = atom({
  key: "onTierCheckState",
  default: false,
});

export const currentTierState = atom<number>({
  key: "currentTierState",
  default: 1,
});

export const shuffleInitialState = atom<boolean>({
  key: "shuffleInitialState",
  default: false,
});

export const changeMissionCheckState = atom({
  key: "changeMissionCheckState",
  default: true,
});

export const randomMissionCheckState = atom({
  key: "randomMissionCheckState",
  default: false,
});

export const resetMissionCheckState = atom({
  key: "resetMissionCheckState",
  default: false,
});

// options
export const rangeCheckState = atom({
  key: "rangeCheckState",
  default: false,
});

export const injeongCheckState = atom({
  key: "injeongCheckState",
  default: false,
});

export const attackCheckState = atom({
  key: "attackCheckState",
  default: false,
});

export const mannerCheckState = atom({
  key: "mannerCheckState",
  default: false,
});

export const oneHitWordCheckState = atom({
  key: "oneHitWordCheckState",
  default: false,
});

// end options

export const shMisTypeState = atom<string>({
  key: "shMisTypeState",
  default: "theory",
});

export const missionValueState = atom<string>({
  key: "missionValueState",
  default: "가",
});
