import json
import os
from typing import Dict, List, Tuple, Optional
from openai import OpenAI
from django.conf import settings
from users.models import UserSelloingInfo


class TopicGenerationService:
    """주제 생성 서비스"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _get_user_info(self, user) -> Dict[str, Optional[str]]:
        """사용자 정보 가져오기"""
        try:
            seloing_info = user.seloing_infos.first()
            return {
                "goal": seloing_info.goal if seloing_info else None,
                "job": seloing_info.job if seloing_info else None,
                "interest": seloing_info.interest if seloing_info else None,
            }
        except Exception:
            return {"goal": None, "job": None, "interest": None}

    def _create_prompt(self, user_info: Dict[str, Optional[str]]) -> str:
        """프롬프트 생성"""
        goal = user_info.get("goal", "").strip() if user_info.get("goal") else None
        job = user_info.get("job", "").strip() if user_info.get("job") else None
        interest = (
            user_info.get("interest", "").strip() if user_info.get("interest") else None
        )

        # 프로필 정보가 있는 경우
        if goal or job or interest:
            prompt = f"""
Generate exactly 3 Korean-language topics for a presentation/speech practice session.

User Info:
- Goal: {goal or '정보없음'}
- Job/Major: {job or '정보없음'}
- Interests: {interest or '정보없음'}

Generation Plan (think silently, output JSON only):
A) Expand a 3-step idea path from the user's profile (e.g., Role → Condition → Insight → Program/Action).
B) Build at least 6 candidate topics by sampling from different branches of that path.
C) Select 3 with maximal mutual diversity across at least two of these axes: perspective (personal/market/policy), time horizon (past/present/future), and actionability (prepare/execute/retrospect).
D) Avoid boilerplate openings and banned phrases.

Constraints:
1) One topic must relate to the user's job/major and align with their goal.
2) Two topics must relate to the user's interests.
3) Each topic must be concrete, engaging, and suitable for a 2–3 minute speech.
4) Topics must enable sharing personal experiences or opinions.
5) Keep them easy for the general public (not overly technical).
6) The response must be ONLY valid JSON without any extra text, markdown, or formatting.
7) Do NOT include special characters, emojis, or line breaks that could break JSON parsing.
8) Output format (exactly): {{"topic1":"주제1","topic2":"주제2","topic3":"주제3"}}

Diversity Controls:
- diversity_key: {int(__import__('time').time())}  # replace per call

Banned phrases (at the beginning of topics): ["예비창업가로서", "소개", "개요", "발표할 내용은", "이 글에서는"]

Selection rules:
- Topics must come from different branches of the idea path.
- If any topic overlaps with previously_used_topics (semantic or near-duplicate), replace it with another branch topic.
"""

        else:
            prompt = """
Generate exactly 3 casual and comfortable topics for presentation/speech practice.

Requirements:
1. Topics should be everyday subjects that anyone can easily talk about.
2. Allow the speaker to freely share personal experiences or thoughts.
3. Each topic should be specific, interesting, and suitable for a 2–3 minute speech.
4. Write in Korean.
5. The response must be ONLY valid JSON without any extra text, markdown, or formatting.
6. Do NOT include special characters, emojis, or line breaks inside the topic strings that could break JSON parsing.
7. The only allowed output format is exactly:
{"topic1": "주제1", "topic2": "주제2", "topic3": "주제3"}

Example topic types:
- Personal experiences (travel, hobbies, memorable moments, etc.)
- Daily life (food, seasons, lifestyle habits, etc.)
- Values or beliefs (dreams, goals, what you consider important, etc.)
"""

        return prompt

    def generate_topics(self, user) -> Tuple[str, str, str]:
        """주제 생성 (동기)"""
        try:
            user_info = self._get_user_info(user)
            prompt = self._create_prompt(user_info)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert who helps users practice speeches by suggesting engaging and relevant topics.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=500,
            )

            # JSON 응답 파싱
            content = response.choices[0].message.content.strip()

            # JSON 파싱 시도
            try:
                topics_data = json.loads(content)
                return (
                    topics_data.get("topic1", "오늘의 날씨와 기분"),
                    topics_data.get("topic2", "가장 좋아하는 음식과 그 이유"),
                    topics_data.get("topic3", "최근 읽은 책이나 본 영화"),
                )
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 주제 반환
                return (
                    "내가 가장 행복했던 순간",
                    "요즘 관심있는 취미나 활동",
                    "10년 후 나의 모습",
                )

        except Exception:
            # API 호출 실패 시 기본 주제 반환
            return (
                "나의 하루 루틴 소개하기",
                "좋아하는 계절과 그 이유",
                "친구들에게 추천하고 싶은 것",
            )


# 동기 함수 래퍼
def generate_topics_sync(user):
    """동기 방식으로 주제 생성"""
    service = TopicGenerationService()
    return service.generate_topics(user)
