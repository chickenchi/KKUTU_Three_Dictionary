from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from collections import Counter

class WordDB:
    def setting(self):
        engine = create_engine('mysql+pymysql://root:1234@localhost/KKUTU', echo=False)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        print("connect ok")

    def __init__(self):
        self.setting()

    def get_hangul_range(self, first_letter):
        """한글 자음에 따른 유니코드 범위 반환"""
        ranges = {
            'ㄱ': ('가', '낗'),
            'ㄴ': ('나', '닣'),
            'ㄷ': ('다', '딯'),
            'ㄹ': ('라', '맇'),
            'ㅁ': ('마', '밓'),
            'ㅂ': ('바', '삫'),
            'ㅅ': ('사', '앃'),
            'ㅇ': ('아', '잏'),
            'ㅈ': ('자', '짛'),
            'ㅊ': ('차', '칳'),
            'ㅋ': ('카', '킿'),
            'ㅌ': ('타', '팋'),
            'ㅍ': ('파', '핗'),
            'ㅎ': ('하', '힣')
        }
        return ranges.get(first_letter, (None, None))
    
    def find_word(self, dto):
        first_letter = dto.word[0]
        item_letter = dto.word[1]
        subject = dto.subject

        if first_letter == None:
            first_letter = ""
        
        if item_letter == None:
            item_letter = ""

        sql = ""
        rangeSet = ""
        options = ""
        
        range = dto.checklist[0] if dto.checklist and len(dto.checklist) > 0 else False
        isKnown = dto.checklist[1] if dto.checklist and len(dto.checklist) > 1 else False
        isInjeong = dto.checklist[2] if dto.checklist and len(dto.checklist) > 2 else False
        isOneHitWord = dto.checklist[3] if dto.checklist and len(dto.checklist) > 3 else False
        isManner = dto.checklist[4] if dto.checklist and len(dto.checklist) > 4 else False
        isAttack = dto.checklist[5] if dto.checklist and len(dto.checklist) > 5 else False

        if first_letter != '' and first_letter in 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ':
            start, end = self.get_hangul_range(first_letter)

            rangeSet = f"""
                Word.word >= '{start}' AND Word.word <= '{end}'
            """

        if range:
            min = range.split("~")[0]
            max = range.split("~")[1]

            options += f"""AND CHAR_LENGTH(Word.word) >= {min}
            AND CHAR_LENGTH(Word.word) <= {max}
            """
        if isKnown:
            options += "AND checked = true\n"
        if isInjeong:
            options += "AND injeong = false\n"
        if subject != 'all':
            options += f"AND subject = '{subject}'\n"
            subjectSet = "JOIN WordSubject ON Word.word = WordSubject.word"
        else:
            subjectSet = ""

        dontGive = False

        if dontGive:
            options += """
                AND (
                word LIKE '%g'
                OR word LIKE '%j'
                OR word LIKE '%k'
                OR word LIKE '%q'
                OR word LIKE '%r'
                OR word LIKE '%u'
                OR word LIKE '%v'
                OR word LIKE '%w'
                OR word LIKE '%x'
                OR word LIKE '%y'
                OR word LIKE '%z'
                )
            """

        if isOneHitWord:
            oneHitWordInitial = self.oneHitWordInitial(isOneHitWord)
            options += oneHitWordInitial

        if isManner:
            mannerShieldInitial = self.mannerShieldInitial(first_letter, item_letter, options, subjectSet)
            options += mannerShieldInitial
        
        if isAttack:
            attackInitial = self.attack(first_letter, item_letter, options, subjectSet)
            options += attackInitial

        if dto.type == 'hardAttack':
            sql = self.hardAttack(first_letter, item_letter, rangeSet, options, subjectSet)
        elif dto.type == 'neutralAttack':
            sql = self.neutral_attack(first_letter, item_letter, options, subjectSet)
        elif dto.type == 'mission':
            if first_letter != "" and first_letter[0] not in 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ':
                sql = f"""
                    SELECT first_letter_count('{first_letter[0]}');
                """

                count = self.session.execute(text(sql)).fetchall()
                count = count[0][0]
            else:
                count = 1000

            if dto.shMisType == 'value':
                return self.valueMission(count, first_letter, item_letter, dto.mission, rangeSet, options, subjectSet)
            sql = self.mission(first_letter, item_letter, dto.mission, rangeSet, dto.shMisType, options, subjectSet)
        elif dto.type == 'allMission':
            sql = self.allMission(first_letter, item_letter, rangeSet, dto.tier, options, subjectSet)
        elif dto.type == 'protect':
            sql = self.protect(first_letter, item_letter, rangeSet, options, subjectSet)
        elif dto.type == 'villain':
            sql = self.villain(first_letter, item_letter, dto.backWord, rangeSet, options, subjectSet)
        elif dto.type == 'long':
            sql = self.long(first_letter, item_letter, rangeSet, options, subjectSet)

        result = self.session.execute(text(sql)).fetchall()
        return result
    
    def oneHitWordInitial(self, isOneHitWord):
        one_hit_list = [
            '녘','꾼','늄','뜩','것','뿐','읖','뿟','렛','켓','펫','슝','렁','걍','륨','슭','슛','슨',
            '겡','럽','쯤','먕','욷','쩐','썹','껸','밈','븜','븨','싶','욤','뮴','씸','틤','껏','셤',
            '믐','쁨','쑴','켠','낏','꾜','텝','븀','럴','흴','캣','튠','듈','눔','휵','냔','냘','픈',
            '꼍','쿄','꼇','튐','귿','읒','읗','탉','묑','엣','읃','뗌','믄','듐','븐','튬','룅','츨',
            '탸','탓','럿','엌','슥','숱','츰','쥬','뜽','칮','곬','틋','깥','픔','줴','륀','됭','렝',
            '핌','윰','픗','듸','읏','쭘','갗','몃','욹','및','찟','텟','룀','뼉','콫','톹','죌','쾃',
            '윅','깆','찱','팎','걔','씃','쩜','덟','볜','얏','랖','줅','퓸','촨','쯕','긔','뎬','꼉',
            '돐','밗','읓','숑','냑','뮨','낵','켸','읔','앝','읕','팁','끠','겊'
        ]

        # 시작
        oneHitWordInitials = "AND "

        if isOneHitWord:
            oneHitWordInitials += "(\nWord.word LIKE '궰'\n"
        else:
            oneHitWordInitials += "NOT (\n"

        # 리스트 기반으로 조건 추가
        for ch in one_hit_list:
            oneHitWordInitials += f"OR Word.word LIKE '%{ch}'\n"

        oneHitWordInitials += ")\n"

        return oneHitWordInitials

    def mannerShieldInitial(self, front_initial1, front_initial2, options, subjectSet):
        rangeSet = f"""
        (
            Word.word LIKE '{front_initial1}%' OR
            Word.word LIKE '{front_initial2}%'
        )
        """
            
        back_initials = self.getBackInitials(rangeSet, options, subjectSet)

        mannerShieldInitials = """
            AND NOT (
            Word.word LIKE '궰'
        """

        for back_initial in back_initials:
            sql = f"""
                SELECT COUNT(*)
                FROM word
                WHERE (
                word LIKE '{back_initial[0]}%'
                OR word LIKE CONCAT(getDoumChar('{back_initial[0]}'), '%')
                ) AND (
                    CHAR_LENGTH(word) > 1
                )
            """

            result = self.session.execute(text(sql)).fetchall()

            if result[0][0] < 10:
                mannerShieldInitials += f"""
OR Word.word LIKE '%{back_initial[0]}'"""

        mannerShieldInitials += """
)"""

        return mannerShieldInitials
    
    def neutral_attack(self, front_initial1, front_initial2, options, subjectSet):
        print(subjectSet)

        exclude_block = """
'값', '갠', '갬', '갭', '걱', '걷', '겅', '겐', '겜', '겟', '겪', '겯', '겻', '곗', '곶', '괌', '괏', '괜', '괫', '괵', '굄', '굇', '굶', '귄', '깅', '깬', '껀', '껴', '꽤', '꿔', '꿸', '뀀', '뀌', '끕', '끗', '낀', '낌', '낡', '낳', '냬', '넋', '넛', '넴', '녜', '놈', '놉', '놓', '뇔', '뇟', '눋', '눕', '눗', '눙', '뉨', '뉫', '늣', '늬', '랙', '랠', '랬', '럭', '럼', '렐', '렘', '룸', '룹', '룻', '뤄', '뤽', '륄', '닦', '닿', '댈', '댐', '댑', '댔', '댜', '덮', '뎀', '돔', '돕', '돚', '돝', '돠', '돤', '둠', '둡', '뒝', '뒨', '뒴', '듣', '듭', '듯', '딘', '딤', '딥', '딲', '땃', '땜', '땟', '떰', '뗀', '뙈', '뚫', '띔', '띰', '띳', '많', '맙', '맡', '맬', '맺', '며', '몌', '묀', '묄', '묏', '묫', '묻', '뭄', '뮈', '뮌', '믈', '믹', '밝', '밟', '밧', '밸', '뱁', '뱌', '뱟', '벗', '벚', '벰', '벳', '봅', '봐', '뵈', '뵐', '뵘', '붐', '붗', '뷜', '뺌', '뻗', '뻰', '뼁', '뼘', '뼛', '뽄', '뽐', '뽑', '뿜', '쁠', '삔', '삵', '삶', '샴', '샷', '섞', '섰', '션', '셜', '셧', '셴', '솝', '솽', '쇤', '쇰', '숀', '숄', '숍', '숏', '숲', '숴', '쉐', '쉰', '쉼', '쉽', '슁', '슘', '슷', '쌤', '쏜', '쏨', '쏭', '쐬', '쑈', '쑨', '쑷', '씌', '씬', '씹', '앰', '앱', '얀', '얍', '얹', '얻', '없', '엊', '엷', '옜', '옮', '옳', '왠', '욀', '욋', '욘', '욥', '웍', '웡', '웰', '윔', '윽', '읫', '잃', '있', '잽', '젉', '젬', '졔', '좃', '좆', '좇', '좋', '좡', '좨', '좽', '줍', '줏', '쥣', '즌', '즐', '즘', '즙', '짙', '쨈', '쫌', '찾', '챈', '챌', '챔', '챗', '쳄', '쳉', '쳐', '쵤', '췻', '칫', '캅', '캔', '캬', '캰', '컵', '켄', '켐', '켜', '켯', '콥', '쾟', '쾰', '퀘', '큘', '킨', '킵', '탠', '탬', '탭', '텀', '템', '톄', '톳', '톺', '툇', '툰', '툼', '튈', '튕', '튤', '틴', '팃', '팟', '팻', '퍄', '퍙', '펌', '폿', '푀', '퓐', '퓰', '핏', '핸', '헴', '헵', '헹', '횃', '횔', '횟', '훑', '훙', '훠', '휜', '휠', '휫', '흄', '흣', '흩', '흭', '힁', '힉', '힙','녘','꾼','늄','뜩','것','뿐','읖','뿟','렛','켓','펫','슝','렁','걍','륨','슭','슛','슨',
'겡','럽','쯤','먕','욷','쩐','썹','껸','밈','븜','븨','싶','욤','뮴','씸','틤','껏','셤',
'믐','쁨','쑴','켠','낏','꾜','텝','븀','럴','흴','캣','튠','듈','눔','휵','냔','냘','픈',
'꼍','쿄','꼇','튐','귿','읒','읗','탉','묑','엣','읃','뗌','믄','듐','븐','튬','룅','츨',
'탸','탓','럿','엌','슥','숱','츰','쥬','뜽','칮','곬','틋','깥','픔','줴','륀','됭','렝',
'핌','윰','픗','듸','읏','쭘','갗','몃','욹','및','찟','텟','룀','뼉','콫','톹','죌','쾃',
'윅','깆','찱','팎','걔','씃','쩜','덟','볜','얏','랖','줅','퓸','촨','쯕','긔','뎬','꼉',
'돐','밗','읓','숑','냑','뮨','낵','켸','읔','앝','읕','팁','끠','겊','가', '각', '간', '갈', '감', '갑', '갓', '강', '갖', '개', '객', '갤', '갯', '갸', '걀', '거', '건', '걸', '검', '겉', '게', '겨', '격', '견', '결', '겹', '경', '곁', '계', '고', '곡', '곤', '곧', '골', '곰', '공', '과', '관', '광', '괘', '괴', '교', '구', '국', '군', '굵', '굼', '굿', '귀', '귓', '규', '귤', '그', '근', '글', '금', '급', '기', '긴', '길', '김', '깃', '깊', '까', '깍', '깔', '깜', '깨', '꺼', '껄', '껍', '께', '꼬', '꼰', '꼴', '꼽', '꽁', '꽃', '꾀', '꾸', '꿀', '꿈', '끄', '끈', '끌', '끝', '끼', '나', '낚', '난', '날', '남', '납', '낱', '내', '냅', '냉', '너', '넉', '넝', '네', '넬', '넵', '년', '노', '녹', '논', '놀', '놋', '농', '뇌', '누', '눈', '뉴', '느', '는', '늘', '늙', '능', '늦', '늪', '니', '닐', '다', '단', '달', '담', '답', '당', '대', '댄', '더', '던', '덜', '덤', '덧', '덩', '데', '덴', '뎅', '도', '독', '돈', '돋', '돌', '돗', '동', '돛', '되', '된', '두', '둘', '둥', '뒤', '뒷', '듀', '드', '든', '들', '등', '디', '딕', '따', '딱', '딴', '딸', '땅', '때', '땍', '땔', '땡', '떡', '떨', '떼', '뗑', '똥', '뙤', '뚜', '뜨', '뜬', '뜯', '띠', '라', '란', '램', '랭', '러', '레', '렉', '로', '록', '롤', '롱', '루', '룰', '뤼', '류', '르', '리', '링', '마', '막', '만', '맏', '말', '맘', '망', '맞', '매', '맥', '맨', '머', '먹', '멀', '멍', '메', '멘', '멜', '멧', '면', '모', '목', '몰', '몸', '몽', '무', '문', '물', '뭇', '므', '미', '민', '밀', '바', '박', '반', '발', '밤', '밥', '방', '밭', '배', '백', '뱃', '뱅', '버', '벅', '번', '벋', '벌', '범', '벙', '베', '벡', '벤', '벨', '벵', '벼', '별', '병', '보', '복', '본', '볼', '봄', '봉', '부', '북', '분', '불', '붉', '붓', '붕', '뷰', '브', '블', '비', '빅', '빈', '빌', '빗', '빙', '빚', '빛', '빤', '빨', '빵', '빼', '뺑', '뻐', '뻔', '뻘', '뻥', '뽀', '뾰', '뿌', '뿔', '삐', '삥', '사', '삯', '산', '살', '삼', '삽', '삿', '상', '새', '색', '샐', '샛', '생', '샤', '섀', '서', '석', '선', '섣', '설', '섬', '섯', '성', '세', '섹', '센', '셀', '셉', '셰', '셸', '솁', '소', '속', '손', '솔', '솜', '솟', '쇠', '쇼', '수', '순', '술', '숨', '숫', '숯', '쉴', '슈', '스', '슬', '시', '식', '신', '실', '심', '싱', '싸', '싼', '쌈', '쌍', '쌩', '써', '썰', '썽', '쑤', '쓰', '씨', '씽', '아', '악', '안', '알', '암', '압', '앗', '앞', '애', '액', '앤', '앨', '앵', '야', '약', '얌', '양', '얘', '어', '억', '언', '얼', '엄', '엇', '엎', '에', '엑', '엘', '엠', '엥', '여', '역', '연', '열', '염', '엽', '영', '예', '옌', '옐', '옛', '오', '옥', '온', '올', '옭', '옵', '옹', '옻', '와', '왁', '완', '왈', '왓', '왕', '왜', '외', '왼', '요', '욕', '용', '우', '운', '울', '움', '웃', '워', '원', '월', '웹', '웽', '위', '윈', '윌', '윗', '유', '육', '윷', '으', '은', '응', '의', '이', '익', '인', '일', '임', '입', '잉', '자', '작', '잔', '잠', '잡', '장', '재', '잭', '잼', '잿', '쟁', '저', '적', '전', '절', '젊', '점', '접', '젓', '정', '젖', '제', '젤', '젱', '조', '존', '졸', '좀', '종', '좌', '주', '줄', '중', '쥐', '지', '직', '진', '질', '짐', '집', '짓', '징', '짜', '쨍', '쩌', '쩔', '쩨', '쩽', '쪽', '쭈', '쭐', '쯔', '찌', '찔', '찜', '찡', '차', '찬', '찰', '참', '찻', '창', '채', '책', '처', '천', '철', '첫', '청', '체', '첼', '쳇', '초', '촌', '총', '추', '춘', '출', '춤', '충', '취', '츠', '치', '친', '칠', '침', '칩', '칭', '카', '칸', '칼', '캐', '캘', '캡', '커', '컨', '컬', '컴', '컷', '케', '코', '콕', '콘', '콜', '콤', '콧', '콩', '콰', '쿠', '쿨', '쿼', '퀴', '퀵', '퀸', '큐', '크', '큰', '클', '키', '킥', '킹', '타', '탁', '탄', '탈', '탐', '탑', '태', '택', '터', '턴', '털', '텁', '텅', '테', '텐', '텔', '토', '톨', '톰', '톱', '통', '퇴', '투', '툴', '튜', '트', '티', '팀', '파', '판', '팔', '팜', '패', '팬', '퍼', '펀', '펄', '페', '펙', '펜', '펠', '펩', '펭', '편', '평', '폐', '포', '폭', '폰', '폴', '표', '푸', '푼', '풀', '품', '풋', '풍', '프', '플', '피', '픽', '필', '하', '한', '할', '함', '합', '핫', '항', '해', '핵', '핼', '햇', '행', '향', '허', '헌', '헐', '헛', '헝', '헤', '헥', '헨', '헬', '현', '협', '호', '혹', '혼', '홀', '홈', '홉', '홑', '화', '환', '활', '황', '홰', '횅', '회', '횡', '후', '훈', '훌', '훨', '훼', '휑', '휘', '휴', '흐', '흔', '흘', '흙', '흠', '흡', '흥', '희', '흰', '히', '힐', '힘', '힝',
'래','량','녀','료','령','룡','륙','림','립'
"""

        sql = f"""
            SELECT word
            FROM word
            {subjectSet}
            WHERE 
            (
            Word.word LIKE '{front_initial1}%' OR
            Word.word LIKE '{front_initial2}%'
            )
            AND (
                CHAR_LENGTH(word) > 1
            )
            AND RIGHT(word, 1) NOT IN (
                {exclude_block}
            )
            {options}
        """

        return sql

    def attack(self, front_initial1, front_initial2, options, subjectSet):
        rangeSet = f"""
        (
            Word.word LIKE '{front_initial1}%' OR
            Word.word LIKE '{front_initial2}%'
        )
        """
            
        back_initials = self.getBackInitials(rangeSet, options, subjectSet)

        attackInitials = """
            AND NOT (
            Word.word LIKE '궰'
        """

        for back_initial in back_initials:
            sql = f"""
                SELECT COUNT(*)
                FROM word
                WHERE (
                word LIKE '{back_initial[0]}%'
                OR word LIKE CONCAT(getDoumChar('{back_initial[0]}'), '%')
                ) AND (
                    CHAR_LENGTH(word) > 1
                )
            """

            result = self.session.execute(text(sql)).fetchall()

            if result[0][0] == 0 or result[0][0] > 33:
                attackInitials += f"""
                OR Word.word LIKE '%{back_initial[0]}'
                """

        attackInitials += """
    )"""

        return attackInitials
    
    def hardAttack(self, front_initial1, front_initial2, rangeSet, options, subjectSet):
        if not rangeSet:
            rangeSet = f"""
            (
                Word.word LIKE '{front_initial1}%' OR
                Word.word LIKE '{front_initial2}%'
            )
        """

        sql = f"""
                SELECT *
                FROM word
                {subjectSet}
                WHERE EXISTS (
                    SELECT 1
                    FROM HardAttackInitial a
                    WHERE Word.word LIKE CONCAT('%', a.initial)
                )
                AND {rangeSet}
                {options}
                ORDER BY CHAR_LENGTH(Word.word) DESC;
            """

        return sql
        
    def mission(self, front_initial1, front_initial2, mission, rangeSet, shMisType, options, subjectSet):
        if mission == "":
            if not rangeSet:
                rangeSet = f"""
                (
                    Word.word LIKE '{front_initial1}%' OR
                    Word.word LIKE '{front_initial2}%'
                )
            """

            sql = f"""
                SELECT Word.word,
                MaxCountCharacter(Word.word) AS mission,
                CHAR_LENGTH(Word.word) AS len,
                checked
                FROM word
{subjectSet}
                WHERE {rangeSet}
                {options}
                ORDER BY mission DESC, len DESC
                LIMIT 1000;
            """
        elif front_initial1 == "":
            if not rangeSet:
                rangeSet = f"""
                Word.word LIKE '%'
            """
                
            sql = f"""
                SELECT
                Word.word,
                (CountCharacter(Word.word, '{mission}'))
                AS mission,
                RANK() OVER (ORDER BY 
                    (CountCharacter(Word.word, '{mission}')) DESC,
                    CHAR_LENGTH(Word.word) DESC)
                AS ranking,
                checked
                FROM word
                {subjectSet}
                WHERE {rangeSet}
                {options}
                LIMIT 1000;
            """

        elif shMisType == 'theory':
            if not rangeSet:
                rangeSet = f"""
                (
                    LEFT(Word.word, {len(front_initial1)}) = '{front_initial1}'
                    OR LEFT(Word.word, {len(front_initial1)}) = '{front_initial2}'
                )
            """

            sql = f"""
                SELECT
                Word.word,
                (CountCharacter(Word.word, '{mission}'))
                AS mission,
                RANK() OVER (ORDER BY 
                    (CountCharacter(Word.word, '{mission}')) DESC,
                    CHAR_LENGTH(Word.word) DESC)
                AS ranking,
                checked
                FROM word
                {subjectSet}
                WHERE {rangeSet}
                {options}
                LIMIT 10;
            """

        elif shMisType == 'reflect':
            if not rangeSet:
                rangeSet = f"""
                (
                    LEFT(Word.word, {len(front_initial1)}) = '{front_initial1}'
                    AND RIGHT(Word.word, {len(front_initial1)}) = '{front_initial1}'
                    OR LEFT(Word.word, {len(front_initial1)}) = '{front_initial2}'
                    AND RIGHT(Word.word, {len(front_initial1)}) = '{front_initial2}'
                )
            """

            sql = f"""
                SELECT
                Word.word,
                (CountCharacter(Word.word, '{mission}'))
                AS mission,
                RANK() OVER (ORDER BY 
                    (CountCharacter(Word.word, '{mission}')) DESC,
                    CHAR_LENGTH(Word.word) DESC)
                AS ranking,
                checked
                FROM word
                {subjectSet}
                WHERE {rangeSet}
                {options}
                LIMIT 10;
            """

        return sql
    
    def get_initial_data(self, back_initial):
        sql = f"""
            SELECT *
            FROM initialScore
            WHERE initial = '{back_initial}'
        """
    
        try:
            result = self.session.execute(text(sql)).fetchall()
            return result
        
        except Exception as e:
            print(f"Error: {e}")
            return ["문제가 발생하였습니다."]

    def get_calculated_value(self, count, back_initial, chain):
        if '가' <= back_initial <= '힣':
            sql = f"""
                SELECT 
                    word,
                    CAST(calculate_value_by_value(word, GREATEST(
                        CountCharacter(word, '가'),
                        CountCharacter(word, '나'),
                        CountCharacter(word, '다'),
                        CountCharacter(word, '라'),
                        CountCharacter(word, '마'),
                        CountCharacter(word, '바'),
                        CountCharacter(word, '사'),
                        CountCharacter(word, '아'),
                        CountCharacter(word, '자'),
                        CountCharacter(word, '차'),
                        CountCharacter(word, '카'),
                        CountCharacter(word, '타'),
                        CountCharacter(word, '파'),
                        CountCharacter(word, '하')
                    ), 1, {count}) AS SIGNED) AS max_score
                FROM 
                    Word
                WHERE 
                    word LIKE '{back_initial}%'
                    OR word LIKE CONCAT(getDoumChar('{back_initial}'), '%')
                ORDER BY 
                    max_score DESC
                LIMIT 1;
            """
        else:
            sql = f"""
                SELECT 
                    word,
                    CAST(GREATEST(
                        calculate_value(word, 'a', {chain}, {count}),
                        calculate_value(word, 'b', {chain}, {count}),
                        calculate_value(word, 'c', {chain}, {count}),
                        calculate_value(word, 'd', {chain}, {count}),
                        calculate_value(word, 'e', {chain}, {count}),
                        calculate_value(word, 'f', {chain}, {count}),
                        calculate_value(word, 'g', {chain}, {count}),
                        calculate_value(word, 'h', {chain}, {count}),
                        calculate_value(word, 'i', {chain}, {count}),
                        calculate_value(word, 'j', {chain}, {count}),
                        calculate_value(word, 'k', {chain}, {count}),
                        calculate_value(word, 'l', {chain}, {count}),
                        calculate_value(word, 'm', {chain}, {count}),
                        calculate_value(word, 'n', {chain}, {count}),
                        calculate_value(word, 'o', {chain}, {count}),
                        calculate_value(word, 'p', {chain}, {count}),
                        calculate_value(word, 'q', {chain}, {count}),
                        calculate_value(word, 'r', {chain}, {count}),
                        calculate_value(word, 's', {chain}, {count}),
                        calculate_value(word, 't', {chain}, {count}),
                        calculate_value(word, 'u', {chain}, {count}),
                        calculate_value(word, 'v', {chain}, {count}),
                        calculate_value(word, 'w', {chain}, {count}),
                        calculate_value(word, 'x', {chain}, {count}),
                        calculate_value(word, 'y', {chain}, {count}),
                        calculate_value(word, 'z', {chain}, {count})
                    ) AS SIGNED) AS max_score
                FROM 
                    Word
                WHERE 
                    word LIKE '{back_initial}%'
                    OR word LIKE CONCAT(getDoumChar('{back_initial}'), '%')
                ORDER BY 
                    max_score DESC
                LIMIT 1;
            """
    
        try:
            result = self.session.execute(text(sql)).fetchall()

            if result == []:
                self.saveBackWordScore(back_initial, 0)
            else:
                self.saveBackWordScore(back_initial, result[0][1])
            return result

        except Exception as e:
            print(f"Error: {e}")
            return ["문제가 발생하였습니다."]  

    def saveBackWordScore(self, back_initial, score):
        sql = f"""
            INSERT INTO initialScore
            VALUES('{back_initial}', '{score}')
        """

        try:
            result = self.session.execute(text(sql))
            self.session.commit()
            print(f"Rows affected: {result}")
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
     
    def removeBackWordScore(self, back_initial):
        sql = f"""
            DELETE FROM initialScore
            WHERE word = '{back_initial}'
        """

        try:
            result = self.session.execute(text(sql))
            self.session.commit()
            print(f"Rows affected: {result}")
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")

    def getBackInitials(self, rangeSet, options, subjectSet):
        sql = f"""
            SELECT RIGHT(Word.word, 1)
            FROM word
            {subjectSet}
            WHERE {rangeSet}
            {options}
        """

        try:
            result = self.session.execute(text(sql)).fetchall()
            return result

        except Exception as e:
            print(f"Error: {e}")
            return ["문제가 발생하였습니다."]

    def valueMission(self, count, front_initial1, front_initial2, mission, rangeSet, options, subjectSet):
        chain = 1

        if not rangeSet:
            rangeSet = f"""
            (
                LEFT(word, {len(front_initial1)}) = '{front_initial1}'
                OR LEFT(word, {len(front_initial1)}) = '{front_initial2}'
            )
        """

        result = self.getBackInitials(rangeSet, options, subjectSet)
        
        rsList = {}
        
        for back_initial in result:
            back_initial = back_initial[0]
            res = self.get_initial_data(back_initial)

            if res != []:
                rsList[back_initial] = res[0][1]
            else:
                rs = self.get_calculated_value(count, back_initial, chain)
                
                if rs == []:
                    rsList[back_initial] = 0
                else:
                    rsList[back_initial] = rs[0][1]

        sql = f"""
            SELECT
                word,
                CAST(calculate_value(word, '{mission}', 1, {count}) AS SIGNED) AS score,
                RIGHT(word, 1) AS last_char,
                checked,
                getDoumChar(RIGHT(word, 1)) AS doum_char
            FROM word
            {subjectSet}
            WHERE {rangeSet}
            {options}
        """

        res = []
        
        try:
            res = self.session.execute(text(sql)).fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return ["문제가 발생하였습니다."]
        
        for i in range(len(res) - 1, -1, -1):
            resultValue = res[i]
            if rsList[resultValue[2]] == 0:
                del res[i]
            else:
                resultValue = list(resultValue)
                resultValue[1] -= rsList[resultValue[2]]
                resultValue[0] += "(-" + str(rsList[resultValue[2]]) + ")"
                res[i] = tuple(resultValue)

        return sorted(res, key=lambda x: x[1], reverse=True)
    
    def allMission(self, front_initial1, front_initial2, rangeSet, tier, options, subjectSet):
        if not rangeSet:
            rangeSet = f"""
            (
                LEFT(word, {len(front_initial1)}) = '{front_initial1}'
                OR LEFT(word, {len(front_initial1)}) = '{front_initial2}'
            )
        """

        if 'a' <= front_initial1 <= 'z':
            sql = f"""
                WITH CountMissions AS (
                    SELECT word, 'a' AS mission_letter, CountCharacter(word, 'a') AS letter_count, CHAR_LENGTH(Word.word) AS word_length, checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'b', CountCharacter(word, 'b'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'c', CountCharacter(word, 'c'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'd', CountCharacter(word, 'd'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'e', CountCharacter(word, 'e'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'f', CountCharacter(word, 'f'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'g', CountCharacter(word, 'g'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'h', CountCharacter(word, 'h'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'i', CountCharacter(word, 'i'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'j', CountCharacter(word, 'j'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'k', CountCharacter(word, 'k'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'l', CountCharacter(word, 'l'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'm', CountCharacter(word, 'm'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'n', CountCharacter(word, 'n'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'o', CountCharacter(word, 'o'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'p', CountCharacter(word, 'p'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'q', CountCharacter(word, 'q'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'r', CountCharacter(word, 'r'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 's', CountCharacter(word, 's'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 't', CountCharacter(word, 't'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'u', CountCharacter(word, 'u'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'v', CountCharacter(word, 'v'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'w', CountCharacter(word, 'w'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'x', CountCharacter(word, 'x'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'y', CountCharacter(word, 'y'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, 'z', CountCharacter(word, 'z'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                ),
                RankedResults AS (
                    SELECT word, mission_letter, letter_count, word_length, checked, 
                        ROW_NUMBER() OVER (PARTITION BY mission_letter ORDER BY letter_count DESC, word_length DESC) AS ranks 
                    FROM CountMissions
                )
                SELECT word, mission_letter FROM RankedResults WHERE ranks = {tier}
            """

        elif '가' <= front_initial1 <= '힣':
            sql = f"""
                WITH CountMissions AS (
                    SELECT word, '가' AS mission_letter, CountCharacter(word, '가') AS letter_count, CHAR_LENGTH(Word.word) AS word_length, checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '나', CountCharacter(word, '나'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '다', CountCharacter(word, '다'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '라', CountCharacter(word, '라'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '마', CountCharacter(word, '마'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '바', CountCharacter(word, '바'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '사', CountCharacter(word, '사'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '아', CountCharacter(word, '아'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '자', CountCharacter(word, '자'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '차', CountCharacter(word, '차'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '카', CountCharacter(word, '카'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '타', CountCharacter(word, '타'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '파', CountCharacter(word, '파'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                    UNION ALL
                    SELECT word, '하', CountCharacter(word, '하'), CHAR_LENGTH(Word.word), checked FROM word
                    {subjectSet}
                    WHERE {rangeSet} {options}
                ),
                RankedResults AS (
                    SELECT word, mission_letter, letter_count, word_length, checked, 
                        ROW_NUMBER() OVER (PARTITION BY mission_letter ORDER BY letter_count DESC, word_length DESC) AS ranks 
                    FROM CountMissions
                )
                SELECT word, mission_letter FROM RankedResults WHERE ranks = {tier}
            """

        return sql

    def villain(self, front_initial1, front_initial2, back_word, rangeSet, options, subjectSet):
        if not rangeSet:
            rangeSet = f"""
                (
                    BINARY Word.word LIKE '{front_initial1}%{back_word}' OR
                    BINARY Word.word LIKE '{front_initial2}%{back_word}'
                )
            """

        sql = f"""
                SELECT *
                FROM word
                {subjectSet}
                WHERE {rangeSet}
                {options}
                AND CHAR_LENGTH(Word.word) <> 1
                ORDER BY LEFT(Word.word, {len(front_initial1)}) ASC, CHAR_LENGTH(Word.word) DESC
                LIMIT 10000
            """
        
        return sql

    def protect(self, front_initial1, front_initial2, rangeSet, options, subjectSet):
        if not rangeSet:
            rangeSet = f"""
                (
                    Word.word LIKE '%{front_initial1}%' OR
                    Word.word LIKE '%{front_initial2}%'
                )
            """

        sql = f"""
                SELECT *
                FROM Word
                {subjectSet}
                WHERE {rangeSet}
                {options}
                AND CHAR_LENGTH(Word.word) <> 1
                ORDER BY CHAR_LENGTH(Word.word) DESC
                LIMIT 1000
            """
        
        return sql
        
    def long(self, front_initial1, front_initial2, rangeSet, options, subjectSet):
        if not rangeSet:
            rangeSet = f"""
                (
                    Word.word LIKE '{front_initial1}%' OR
                    Word.word LIKE '{front_initial2}%'
                )
            """

        sql = f"""
                SELECT *
                FROM Word
                {subjectSet}
                WHERE {rangeSet}
                {options}
                AND CHAR_LENGTH(Word.word) > 8
                ORDER BY CHAR_LENGTH(Word.word) DESC
                LIMIT 1000
            """
        
        return sql
    
    def precise_find_word(self, word):
        sql = """
        SELECT word, checked
        FROM word
{subjectSet}
        WHERE word = '{0}'
        """.format(word)

        try:
            result = self.session.execute(text(sql)).fetchall()
            return result
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
        
    def initial_max_score(self, dto):
        rangeSet = ""

        word = dto['word']
        chain = dto['chain']

        if word[0] != '' and word[0] in 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ':
            start, end = self.get_hangul_range(word[0])

            rangeSet = f"""
                word >= '{start}' AND word <= '{end}'
            """

        sql = f"""
            SELECT first_letter_count('{word[0]}')
        """

        count = self.session.execute(text(sql)).fetchall()
        count = count[0][0]
        
        if not rangeSet:
            rangeSet = f"""
                (
                    word LIKE '{word[0]}%' OR
                    word LIKE '{word[1]}%'
                )
            """

        if '가' <= word[0] <= '힣':
            sql = f"""
                SELECT 
                word,
                CAST(GREATEST(
                    calculate_value(word, '가', {chain}, {count}),
                    calculate_value(word, '나', {chain}, {count}),
                    calculate_value(word, '다', {chain}, {count}),
                    calculate_value(word, '라', {chain}, {count}),
                    calculate_value(word, '마', {chain}, {count}),
                    calculate_value(word, '바', {chain}, {count}),
                    calculate_value(word, '사', {chain}, {count}),
                    calculate_value(word, '아', {chain}, {count}),
                    calculate_value(word, '자', {chain}, {count}),
                    calculate_value(word, '차', {chain}, {count}),
                    calculate_value(word, '카', {chain}, {count}),
                    calculate_value(word, '타', {chain}, {count}),
                    calculate_value(word, '파', {chain}, {count}),
                    calculate_value(word, '하', {chain}, {count})
                ) AS SIGNED) AS max_score
                FROM 
                    Word
                WHERE 
                    {rangeSet}
                ORDER BY 
                    max_score DESC;
            """
        else:
            sql = f"""
                SELECT 
                word,
                CAST(GREATEST(
                    calculate_value(word, 'a', {chain}, {count}),
                    calculate_value(word, 'b', {chain}, {count}),
                    calculate_value(word, 'c', {chain}, {count}),
                    calculate_value(word, 'd', {chain}, {count}),
                    calculate_value(word, 'e', {chain}, {count}),
                    calculate_value(word, 'f', {chain}, {count}),
                    calculate_value(word, 'g', {chain}, {count}),
                    calculate_value(word, 'h', {chain}, {count}),
                    calculate_value(word, 'i', {chain}, {count}),
                    calculate_value(word, 'j', {chain}, {count}),
                    calculate_value(word, 'k', {chain}, {count}),
                    calculate_value(word, 'l', {chain}, {count}),
                    calculate_value(word, 'm', {chain}, {count}),
                    calculate_value(word, 'n', {chain}, {count}),
                    calculate_value(word, 'o', {chain}, {count}),
                    calculate_value(word, 'p', {chain}, {count}),
                    calculate_value(word, 'q', {chain}, {count}),
                    calculate_value(word, 'r', {chain}, {count}),
                    calculate_value(word, 's', {chain}, {count}),
                    calculate_value(word, 't', {chain}, {count}),
                    calculate_value(word, 'u', {chain}, {count}),
                    calculate_value(word, 'v', {chain}, {count}),
                    calculate_value(word, 'w', {chain}, {count}),
                    calculate_value(word, 'x', {chain}, {count}),
                    calculate_value(word, 'y', {chain}, {count}),
                    calculate_value(word, 'z', {chain}, {count})
                ) AS SIGNED) AS max_score
            FROM 
                Word
            WHERE 
                {rangeSet}
            ORDER BY 
                max_score DESC;
            """

        try:
            result = self.session.execute(text(sql)).fetchall()
            return result
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
    
    def insert_word(self, dto):
        words = dto['word'].splitlines()

        sql = text(f"INSERT IGNORE INTO Word VALUES (:word, 0, '', 1)")

        try:
            result = self.session.execute(
              sql,
              [
                {'word': w}
                for w in zip(words)
              ]
            )
            self.session.commit()
            affected_rows = result.rowcount
            if affected_rows == 0:
                return ["warning", "이미 추가된 단어입니다."]
            else:
                return ["success", f"{affected_rows}개의 단어가 추가되었습니다."]
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
        
    def delete_word(self, word):
        words = word.splitlines()

        sql = text("DELETE FROM word WHERE word = (:word)")

        try:
            result = self.session.execute(sql, [{'word': w} for w in words])
            self.session.commit()
            affected_rows = result.rowcount
            if affected_rows == 0:
                return ["warning", "존재하지 않는 단어입니다."]
            else:
                return ["success", f"{affected_rows}개의 단어가 삭제되었습니다."]
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
        
    def insert_subject(self, dto):
        words = dto['word']
        subject = dto['subject']

        sql = text(f"INSERT IGNORE INTO WordSubject VALUES (:word, :subject)")

        try:
            self.session.execute(
              sql,
              [
                {'word': w, 'subject': s}
                for w, s in zip(words, subject)
              ]
            )
            self.session.commit()
            return ["success", f"주제가 성공적으로 추가되었습니다."]
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
        
    def delete_subject(self, dto):
        words = dto['word']
        subject = dto['subject']

        sql = text(f"DELETE FROM WordSubject WHERE word = :word AND subject = :subject")

        try:
            for w, s in zip(words, subject):
                self.session.execute(sql, {'word': w, 'subject': s})

            self.session.commit()
            return ["success", f"주제가 성공적으로 삭제되었습니다."]
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
        
    def known_word(self, word, checked):
        sql = """
        UPDATE Word
        SET checked = '{1}'
        WHERE word = '{0}'
        """.format(word, 1 - checked)

        try:
            self.session.execute(text(sql))
            self.session.commit()
            return ["success", "표시 완료."]
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
        
    def remember_phrase(self, word, phrase):
        sql = """
        UPDATE Word
        SET sentence = '{1}'
        WHERE word = '{0}'
        """.format(word, phrase)

        try:
            self.session.execute(text(sql))
            self.session.commit()
            return ["success", "표시 완료."]
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
        
    def current_phrase(self, word):
        sql = """
        SELECT sentence
        FROM word
{subjectSet}
        WHERE word = '{0}'
        """.format(word)

        try:
            result = self.session.execute(text(sql)).fetchall()
            return result
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
        
    def uread(self, dto):
        try:
            if isinstance(dto.words, str):
                # 단일 문자열인 경우
                sql = """
                    UPDATE Word
                    SET checked = :isRead
                    WHERE word = :word
                """
                self.session.execute(text(sql), {"isRead": dto.isRead, "word": dto.words})
            else:
                # 리스트인 경우
                for word in dto.words:
                    if '[' in word:
                        word = word.split('] ')[1]
                    sql = """
                        UPDATE Word
                        SET checked = :isRead
                        WHERE word = :word
                    """
                    self.session.execute(text(sql), {"isRead": dto.isRead, "word": word})

            self.session.commit()
            return ["success", "설정 완료."]
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
        
    def all_word(self):
        sql = f"""
        SELECT *
        FROM word
        WHERE word NOT REGEXP '^[a-z]'
        AND CHAR_LENGTH(Word.word) > 1
        """

        try:
            result = self.session.execute(text(sql)).fetchall()
            return result
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
        
    def initial(self):
        sql = f"""
        SELECT *
        FROM LoseInitial;
        """

        try:
            result = self.session.execute(text(sql)).fetchall()
            return result
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            return ["error", "문제가 발생하였습니다."]
        
    def rare_box(self, dto):
        pieces = dto.piece
        highPieces = dto.highPiece
        rarePieces = dto.rarePiece

        highPiecesSetting = ""
        rarePiecesSetting = ""
        elementPieceSetting = ""

        pieceList = ""

        for piece in highPieces:
            pieceItem = piece[0] # 글자 조각
            pieceCount = piece[1] # 개수

            pieceList += pieceItem

            if highPiecesSetting == "":
                highPiecesSetting = f"""
                    (CHAR_LENGTH(word) - CHAR_LENGTH(REPLACE(word, '{pieceItem}', '')))
                """
            else:
                highPiecesSetting += f""" +
                    (CHAR_LENGTH(word) - CHAR_LENGTH(REPLACE(word, '{pieceItem}', '')))
                """

            elementPieceSetting += f"""
                AND (CHAR_LENGTH(word) - CHAR_LENGTH(REPLACE(word, '{pieceItem}', '')) <= {pieceCount})
            """

        for piece in rarePieces:
            pieceItem = piece[0] # 글자 조각
            pieceCount = piece[1] # 개수

            pieceList += pieceItem

            if rarePiecesSetting == "":
                rarePiecesSetting = f"""
                    (CHAR_LENGTH(word) - CHAR_LENGTH(REPLACE(word, '{pieceItem}', '')))
                """
            else:
                rarePiecesSetting += f""" +
                    (CHAR_LENGTH(word) - CHAR_LENGTH(REPLACE(word, '{pieceItem}', '')))
                """

            elementPieceSetting += f"""
                AND (CHAR_LENGTH(word) - CHAR_LENGTH(REPLACE(word, '{pieceItem}', '')) <= {pieceCount})
            """

        for piece in pieces:
            pieceItem = piece[0] # 글자 조각
            pieceCount = piece[1] # 개수

            pieceList += pieceItem

            elementPieceSetting += f"""
                AND (CHAR_LENGTH(word) - CHAR_LENGTH(REPLACE(word, '{pieceItem}', '')) <= {pieceCount})
            """

        if rarePiecesSetting == "": rarePiecesSetting = 0
        if highPiecesSetting == "": highPiecesSetting = 0
          
        sql = f"""
            SELECT word
            FROM Word
            WHERE CHAR_LENGTH(word) = 6
            AND word REGEXP '^[{pieceList}]*$'
            {elementPieceSetting}
            AND
            (
                (
                    -- 고급 글자가 4개인 경우
                    {highPiecesSetting}
                    >= 4
                )
                OR
                ( -- 희귀 글자가 1개이고 고급 글자가 2개인 경우
                    (
                        {rarePiecesSetting}
                    ) >= 1
                    AND 
                    (
                        {highPiecesSetting}
                    ) >= 2
                )
                OR
                ( -- 희귀 글자가 2개일 경우
                    (
                        {rarePiecesSetting}
                    ) >= 2
                )
            );
        """

        result = self.session.execute(text(sql)).fetchall()
        return result
        
    def find_word_by_piece(self, dto):
        pieces = dto.piece

        rare_result = self.rare_box(dto)

        if len(rare_result) != 0:
            print(rare_result)
            return rare_result
        
        if len(pieces) <= 300:
            pieceList = ""

            sql = f"""
                SELECT word
                FROM word
            """ 

            pieceSetting = ""

            for piece in pieces:
                pieceItem = piece[0]
                pieceCount = piece[1]

                pieceList += pieceItem

                pieceSetting += f"""
                    AND CHAR_LENGTH(word) - CHAR_LENGTH(REPLACE(word, '{pieceItem}', '')) BETWEEN 0 AND {pieceCount}
                """

            sql += f"""
                WHERE word REGEXP '^[{pieceList}]*$'
            """

            sql += pieceSetting

            sql += f"""
                AND CHAR_LENGTH(word) <= 6
                ORDER BY CHAR_LENGTH(word) DESC
            """

            try:
                result = self.session.execute(text(sql)).fetchall()
                return result
            except Exception as e:
                self.session.rollback()
                print(f"Error: {e}")
                return ["error", "문제가 발생하였습니다."]
                
        else:
            sql = f"""
            SELECT word
            FROM word
            WHERE CHAR_LENGTH(word) <= 6"""
        
            try:
                result = self.session.execute(text(sql)).fetchall()
            except Exception as e:
                self.session.rollback()
                print(f"Error: {e}")
                return ["error", "문제가 발생하였습니다."]
            
            passedWords = []
            pieceDict = {}

            for piece in pieces:
                pieceDict[piece[0]] = piece[1]
            
            for word in result:
                word = word[0]

                charCount = Counter(word)

                check = True

                for char, count in charCount.items():
                    if char not in pieceDict or pieceDict[char] < count:
                        check = False
                        break

                if check == True:
                    passedWords.append(word)

            return passedWords