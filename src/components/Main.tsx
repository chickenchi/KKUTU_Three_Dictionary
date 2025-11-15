import React, { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";
import axios from "axios";
import { SettingPopup } from "../tools/settingFunction/SettingPopup";
import { getDoumChar } from "./functions/GetDoumChar";
import { WordSettingPopup } from "../tools/wordFunction/WordSettingPopup";
import { useAlarm } from "../tools/alarmFunction/AlarmProvider";
import { Alarm } from "../tools/alarmFunction/AlarmManager";
import { getFromLocalStorage } from "../commonFunctions/LocalStorage";
import { useWaiting } from "../tools/waitFunction/WaitProvider";
import { getValueByLabel } from "../commonFunctions/SubjectOptions";
import { useRecoilState } from "recoil";
import {
  optionState,
  subjectState,
  shMisTypeState,
  resultCountState,
} from "../RecoilAtoms/common/Atom";
import SubjectModal from "../tools/subjectFunction/Subject";
import SubjectButton from "./buttons/SubjectButton";
import { SelectItem } from "./select/SelectItem";
import {
  elementsProps,
  optionDescription,
  optionProps,
} from "./select/props/SelectProps";

const Header = styled.div`
  background-color: white;
  width: 100%;
  height: 88%;

  font-family: "Pretendard";
`;

const Star = styled.svg``;
const UnStar = styled.svg``;

const Known = styled.button`
  background-color: rgba(0, 0, 0, 0);

  border: none;

  margin-right: 5px;
`;

const All = styled.button`
  background-color: rgba(0, 0, 0, 0);

  border: none;

  margin-right: 5px;
`;

const Checkbox = styled.input`
  width: auto;
  height: auto;
  margin-right: 5px;
`;

const RadioTitle = styled.p`
  margin-right: 12px;
  font-size: 13pt;
`;

const Label = styled.label`
  margin-right: 10px;
  color: #111111;
  font-size: 10pt;
`;

const ToolList = styled.div`
  padding-left: 20px;
  padding-top: 20px;

  width: 100%;
  height: 15%;

  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
`;

const RadioList = styled.div`
  width: 100%;
  display: flex;
  padding-bottom: 5px;
`;

const SearchContainer = styled.div`
  width: 100%;
  margin-bottom: 5px;

  display: flex;
  align-items: center;
`;

const SettingButton = styled.button`
  background-color: rgba(10, 10, 10, 0);

  border: none;

  margin-left: 10px;
`;

const Setting = styled.img`
  width: 20px;
  height: 20px;
`;

const RadioContainer = styled.div`
  height: 30px;

  display: flex;
  align-items: center;
`;

const SearchTitle = styled.p`
  margin-right: 12px;
  font-size: 13pt;
`;

const ImportWord = styled.div`
  position: relative;

  margin-top: 20px;
  margin-left: 20px;

  border-radius: 10px;
  width: 95%;
  height: 70%;

  padding-left: 20px;
  padding-top: 20px;

  overflow-y: auto;
  overflow-x: hidden;
`;

const MissionType = styled.div`
  position: absolute;

  right: 20px;
`;

const Word = styled.input`
  width: 150px;
  height: 25px;
  margin-right: 10px;
  padding-left: 5px;

  font-size: 9pt;
  font-family: "Pretendard";
`;

const Mission = styled.input`
  width: 150px;
  height: 25px;
  margin-right: 10px;
  padding-left: 5px;

  font-size: 9pt;
  font-family: "Pretendard";
`;

const SearchButton = styled.button`
  background-color: #719eff;

  width: 68px;
  height: 25px;

  color: white;
  font-size: 9pt;

  border: none;
  border-radius: 4px;

  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease,
    box-shadow 0.2s ease;
  font-family: "Pretendard";

  &:hover {
    background-color: rgba(230, 230, 230);
  }

  &:active {
    background-color: rgba(240, 240, 240);
    transform: scale(0.98);
  }

  &:focus {
    outline: none;
  }
`;

const ResultCount = styled.p`
  margin-left: 5pt;
  font-size: 12pt;
  font-family: "Pretendard";
`;

const Words = styled.button<{ checked: number; rank?: number }>`
  background-color: rgba(0, 0, 0, 0);
  display: block;

  margin-bottom: 5px;
  padding-bottom: 5px;

  border: none;

  color: ${({ checked }) =>
    checked === 0 ? "rgb(80, 80, 80)" : "rgb(160, 160, 160)"};

  font-size: 11pt;
  font-weight: ${({ rank }) => (rank != null && rank <= 3 ? "600" : "0")};
  font-family: "Pretendard";

  &:hover {
    color: rgb(120, 120, 120);
  }
`;

const Main = () => {
  const [selectedOption, setSelectedOption] = useRecoilState(optionState);
  const [resultCount, setResultCount] = useRecoilState(resultCountState);

  const [subjectOption, setSubjectOption] = useRecoilState(subjectState);
  const [wordValue, setWordValue] = useState("");
  const [backWordValue, setBackWordValue] = useState("");
  const [missionValue, setMissionValue] = useState("");
  const [shMisType] = useRecoilState(shMisTypeState);

  const [isTenSec, setIsTenSec] = useState<boolean>(false);
  const [isKnown, setIsKnown] = useState<boolean>(false);
  const [isInjeong, setIsInjeong] = useState<boolean>(false);
  const [isManner, setIsManner] = useState<boolean>(false);
  const [isAttack, setIsAttack] = useState<boolean>(false);
  const [isOneHitWord, setIsOneHitWord] = useState<boolean>(false);
  const [wordList, setWordList] = useState<string[]>([]);

  const [openSetting, setOpenSetting] = useState<boolean>(false);
  const [openWordSetting, setOpenWordSetting] = useState<boolean>(false);

  const [wspProps, getWSPProps] = useState<[string, number]>(["", 0]);

  const wordRef = useRef<HTMLInputElement>(null);
  const backWordRef = useRef<HTMLInputElement>(null);
  const missionRef = useRef<HTMLInputElement>(null);

  const { showAlarm, alarmIcon, alarmDescription, remainedTime } = useAlarm();

  const { setWaiting } = useWaiting();

  const setSubjectChange = (subject: string) => {
    setSubjectOption(subject);
  };

  const handleWordChange = (event: any) => {
    setWordValue(event.target.value);
  };

  const handleBackWordChange = (event: any) => {
    setBackWordValue(event.target.value);
  };

  const handleMissionChange = (event: any) => {
    setMissionValue(event.target.value);
  };

  const handleOpenSettingChange = () => {
    setOpenSetting(!openSetting);
  };

  const handleIsTenSecChange = () => {
    setIsTenSec(!isTenSec);
  };

  const handleIsKnownChange = () => {
    setIsKnown(!isKnown);
  };

  const handleIsInjeongChange = () => {
    setIsInjeong(!isInjeong);
  };

  const handleIsMannerChange = () => {
    setIsManner(!isManner);
  };

  const handleIsAttackChange = () => {
    setIsAttack(!isAttack);
  };

  const handleIsOnHitWordChange = () => {
    setIsOneHitWord(!isOneHitWord);
  };

  useEffect(() => {
    const getElementSearchType = async () => {
      let searchType = await getFromLocalStorage("searchType");
      setSelectedOption(searchType);
    };

    getElementSearchType();
  }, [shMisType]);

  const handleKeyDown = (event: any) => {
    if (event.key === "Enter") {
      event.preventDefault();
      search();
    }
  };

  const activeWSP = (wspProps: [string, number]) => {
    getWSPProps(wspProps);
    setOpenWordSetting(true);
  };

  const showWord = () => {
    let words: React.JSX.Element[];

    if (wordList[0] === "아쉽게도 단어가 없네요...") {
      return wordList[0];
    }

    words = wordList.map((word: any, index: any) => {
      let wordItem = word[0];
      let checked: number;
      let output;
      let rank;
      let figure;

      if (selectedOption === "mission") {
        if (shMisType === "theory") {
          figure = word[1];
          rank = word[2];
          checked = word[3];
        } else if (shMisType === "value") {
          figure = word[1];
          checked = word[2];
        } else {
          figure = word[1];
          checked = word[2];
        }
      } else {
        checked = word[1];
      }

      if (selectedOption === "mission") {
        if (missionValue === "") {
          output = `${wordItem}[${figure}]`;
        } else if (shMisType === "theory") {
          output = `${rank} Tier. ${wordItem}[${figure}]`;
        } else {
          output = `${wordItem}[${figure}]`;
        }
      } else {
        output = `${wordItem}`;
      }

      return (
        <Words
          onClick={() => activeWSP([wordItem, checked])}
          key={index}
          checked={checked}
        >
          {output}
        </Words>
      );
    });

    return words;
  };

  const { setAlarm } = useAlarm();

  const search = async () => {
    try {
      let initialList: string[];

      if (getDoumChar(wordValue) !== "failed") {
        initialList = [wordValue, getDoumChar(wordValue)];
      } else {
        initialList = [wordValue, wordValue];
      }

      let range = "";

      if (isTenSec) {
        range = await getFromLocalStorage("wordRange");
      }

      let checklist = [
        range,
        isKnown,
        isInjeong,
        isOneHitWord,
        isManner,
        isAttack,
      ];

      setWaiting(true);

      const subject = getValueByLabel(subjectOption);

      const response = await axios.post("http://127.0.0.1:5000/word", {
        word: initialList,
        backWord: backWordValue,
        type: selectedOption,
        subject: subject,
        mission: missionValue,
        shMisType: shMisType,
        checklist: checklist,
      });

      console.log(response.data);

      setWaiting(false);

      if (response.data !== "단어 없음") {
        setResultCount(response.data.length);
        setWordList(response.data);
      } else {
        setResultCount(0);
        setWordList(["아쉽게도 단어가 없네요..."]);
      }
    } catch (error) {
      console.log(error);
      setAlarm("error", "데이터를 받아오는 도중 문제가 생겼습니다.");
      setWaiting(false);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey) {
        switch (e.key) {
          case "ArrowLeft":
            e.preventDefault();
            if (wordRef.current) {
              wordRef.current.focus();
              setWordValue("");
            }
            break;
          case "ArrowRight":
            e.preventDefault();

            if (missionRef.current) {
              missionRef.current.focus();
              setMissionValue("");
            } else if (backWordRef.current) {
              backWordRef.current.focus();
              setBackWordValue("");
            }
            break;
        }

        if (e.altKey) {
          switch (e.key) {
            case "t":
              setIsTenSec(!isTenSec);
              break;
            case "k":
              setIsKnown(!isKnown);
              break;
          }
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isTenSec, isKnown]);

  useEffect(() => {
    setTimeout(() => {
      if (wordRef.current) {
        wordRef.current.focus();
      }
    }, 0);
  }, []);

  return (
    <Header className="Header">
      {showAlarm && (
        <Alarm
          iconType={alarmIcon}
          description={alarmDescription}
          remainedTime={remainedTime}
        />
      )}
      {openSetting && <SettingPopup setOpenSetting={setOpenSetting} />}
      {openWordSetting && (
        <WordSettingPopup
          setWordOpenSetting={setOpenWordSetting}
          word={wspProps[0]}
          checked={wspProps[1]}
          Search={search}
        />
      )}
      <SubjectModal setSubjectChange={setSubjectChange} />
      <ToolList>
        <RadioList>
          <RadioContainer>
            <RadioTitle>검색 유형</RadioTitle>
          </RadioContainer>

          <RadioContainer>
            <SelectItem
              elements={optionProps}
              selectState={optionState}
              selectDescription={optionDescription}
            />
            <SubjectButton />

            {isKnown ? (
              <Known onClick={handleIsKnownChange}>
                <Star
                  width="24"
                  height="23"
                  viewBox="0 0 18 17"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M8.99984 14.275L4.84984 16.775C4.66651 16.8916 4.47484 16.9416 4.27484 16.9249C4.07484 16.9083 3.89984 16.8416 3.74984 16.725C3.59984 16.6083 3.48317 16.4626 3.39984 16.288C3.31651 16.1133 3.29984 15.9173 3.34984 15.7L4.44984 10.975L0.774841 7.79995C0.608174 7.64995 0.504174 7.47895 0.462841 7.28695C0.421507 7.09495 0.433841 6.90762 0.499841 6.72495C0.565841 6.54229 0.665841 6.39228 0.799841 6.27495C0.933841 6.15762 1.11717 6.08262 1.34984 6.04995L6.19984 5.62495L8.07484 1.17495C8.15817 0.974951 8.28751 0.824951 8.46284 0.724951C8.63817 0.624951 8.81717 0.574951 8.99984 0.574951C9.18251 0.574951 9.36151 0.624951 9.53684 0.724951C9.71217 0.824951 9.84151 0.974951 9.92484 1.17495L11.7998 5.62495L16.6498 6.04995C16.8832 6.08328 17.0665 6.15828 17.1998 6.27495C17.3332 6.39162 17.4332 6.54162 17.4998 6.72495C17.5665 6.90829 17.5792 7.09595 17.5378 7.28795C17.4965 7.47995 17.3922 7.65062 17.2248 7.79995L13.5498 10.975L14.6498 15.7C14.6998 15.9166 14.6832 16.1126 14.5998 16.288C14.5165 16.4633 14.3998 16.609 14.2498 16.725C14.0998 16.841 13.9248 16.9076 13.7248 16.9249C13.5248 16.9423 13.3332 16.8923 13.1498 16.775L8.99984 14.275Z"
                    fill="black"
                  />
                </Star>
              </Known>
            ) : (
              <All onClick={handleIsKnownChange}>
                <UnStar
                  width="24"
                  height="23"
                  viewBox="0 0 20 19"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M3.86286 16.5866L3.86257 16.5879C3.79129 16.8977 3.80936 17.2115 3.94857 17.5033C4.06476 17.7468 4.23031 17.9543 4.44287 18.1196C4.67383 18.2993 4.94236 18.399 5.23332 18.4232C5.54917 18.4495 5.84664 18.3681 6.11262 18.2004L9.99984 15.8587L13.8866 18.2001C14.1529 18.3688 14.4512 18.4505 14.768 18.4231C15.0577 18.398 15.3253 18.2987 15.5557 18.1205C15.7693 17.9553 15.9352 17.7471 16.0514 17.5026C16.1901 17.2108 16.2085 16.8973 16.137 16.5875L16.1368 16.5866L15.1053 12.1558L18.5517 9.17831L18.5518 9.17835L18.5578 9.173C18.7924 8.96357 18.9599 8.70302 19.0266 8.39318C19.0876 8.10986 19.0688 7.82647 18.9697 7.55408C18.8772 7.29971 18.7321 7.07632 18.5291 6.89866C18.3025 6.70035 18.0188 6.59758 17.7206 6.55498L17.7071 6.55305L17.6935 6.55186L13.1436 6.15316L11.3864 1.98264C11.3862 1.9823 11.3861 1.98195 11.3859 1.9816C11.2634 1.68797 11.0629 1.44938 10.7846 1.29063C10.5419 1.15222 10.2783 1.07495 9.99984 1.07495C9.72141 1.07495 9.4578 1.15222 9.21513 1.29063C8.93679 1.44938 8.73633 1.68796 8.61375 1.98158C8.6136 1.98193 8.61345 1.98229 8.6133 1.98264L6.85606 6.15316L2.30619 6.55186L2.29322 6.553L2.28032 6.55481C1.9815 6.59676 1.69764 6.69985 1.47046 6.89878C1.26715 7.0768 1.12167 7.3002 1.02959 7.55505C0.931366 7.82691 0.913212 8.10963 0.974039 8.39218C1.04056 8.70118 1.20703 8.9616 1.44036 9.1716L1.44029 9.17168L1.44796 9.17831L4.89437 12.1558L3.86286 16.5866Z"
                    stroke="black"
                  />
                </UnStar>
              </All>
            )}

            <Checkbox
              type="checkbox"
              onChange={handleIsTenSecChange}
              checked={isTenSec}
              title="설정에서 제시한 글자 제한으로 단어를 출력합니다."
            />
            <Label
              htmlFor="10s"
              title="설정에서 제시한 글자 제한으로 단어를 출력합니다."
            >
              글자 수 제한
            </Label>
            <Checkbox
              type="checkbox"
              onChange={handleIsInjeongChange}
              checked={isInjeong}
            />
            <Label htmlFor="injeong">노인정</Label>
            {!isOneHitWord && (
              <>
                <Checkbox
                  type="checkbox"
                  onChange={handleIsAttackChange}
                  checked={isAttack}
                  title="받아칠 수 있는 뒷 글자가 1~32개에 해당하는 단어를 출력합니다."
                />
                <Label
                  htmlFor="attack"
                  title="받아칠 수 있는 뒷 글자가 1~32개에 해당하는 단어를 출력합니다."
                >
                  공격 단어
                </Label>
              </>
            )}
            {!isOneHitWord && (
              <>
                <Checkbox
                  type="checkbox"
                  onChange={handleIsMannerChange}
                  checked={isManner}
                  title="이을 수 있는 단어의 개수가 10개 이상인 단어만 출력됩니다."
                />
                <Label
                  htmlFor="manner"
                  title="이을 수 있는 단어의 개수가 10개 이상인 단어만 출력됩니다."
                >
                  매너
                </Label>
              </>
            )}
            {!isManner && !isAttack && (
              <>
                <Checkbox
                  type="checkbox"
                  onChange={handleIsOnHitWordChange}
                  checked={isOneHitWord}
                  title="한 번에 죽는 단어만 출력합니다."
                />
                <Label
                  htmlFor="oneHitWord"
                  title="한 번에 죽는 단어만 출력합니다."
                >
                  한방 단어
                </Label>
              </>
            )}
          </RadioContainer>

          <SettingButton onClick={handleOpenSettingChange}>
            <Setting src="./image/setting.png" />
          </SettingButton>
        </RadioList>

        <SearchContainer>
          <SearchTitle>단어 찾기</SearchTitle>

          {selectedOption === "protect" ? (
            <Word
              type="text"
              value={wordValue}
              placeholder="포함 글자 입력"
              onChange={handleWordChange}
              onKeyDown={handleKeyDown}
              ref={wordRef}
            />
          ) : (
            <Word
              type="text"
              value={wordValue}
              placeholder="앞 글자 입력"
              onChange={handleWordChange}
              onKeyDown={handleKeyDown}
              ref={wordRef}
            />
          )}
          {selectedOption === "villain" && (
            <Word
              type="text"
              value={backWordValue}
              placeholder="뒷 글자 입력"
              onChange={handleBackWordChange}
              onKeyDown={handleKeyDown}
              ref={backWordRef}
            />
          )}
          {selectedOption === "mission" && (
            <Mission
              type="text"
              value={missionValue}
              placeholder="미션 글자 입력"
              onChange={handleMissionChange}
              onKeyDown={handleKeyDown}
              ref={missionRef}
            />
          )}
          <SearchButton onClick={search}>검색</SearchButton>
          {resultCount != 0 && (
            <ResultCount>검색 결과: {resultCount}개</ResultCount>
          )}
        </SearchContainer>
      </ToolList>

      <ImportWord>
        {selectedOption === "mission" && (
          <MissionType>
            <SelectItem elements={elementsProps} selectState={shMisTypeState} />
          </MissionType>
        )}

        {showWord()}
      </ImportWord>
    </Header>
  );
};

export default Main;
