export const subjectOptions = [
  { value: "all", label: "주제 없음" },
  { value: "", label: "--------- 노인정 주제 ---------", disabled: true },
  { value: "economy", label: "경제" },
  { value: "history", label: "역사" },
  { value: "", label: "--------- 어인정 주제 ---------", disabled: true },
  { value: "sanabi", label: "산나비" },
];

export const getValueByLabel = (label: string) => {
  const option = subjectOptions.find((option) => option.label === label);
  return option ? option.value : null; // option이 있으면 value 반환, 없으면 null 반환
};
