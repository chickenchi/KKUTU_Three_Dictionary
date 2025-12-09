export const subjectOptions = [
  { value: "all", label: "주제 없음", injeong: true },
  {
    value: "",
    label: "--------- 노인정 주제 ---------",
    disabled: true,
    injeong: false,
  },
  { value: "economy", label: "경제", injeong: true },
  { value: "history", label: "역사", injeong: true },
  {
    value: "",
    label: "--------- 어인정 주제 ---------",
    disabled: true,
    injeong: false,
  },
  { value: "sanabi", label: "산나비", injeong: false },
  { value: "unesco", label: "유네스코 세계유산", injeong: false },
];

export const getValueByLabel = (label: string) => {
  const option = subjectOptions.find((option) => option.label === label);
  return option ? option.value : null; // option이 있으면 value 반환, 없으면 null 반환
};
