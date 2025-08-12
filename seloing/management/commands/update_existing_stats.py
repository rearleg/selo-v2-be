from django.core.management.base import BaseCommand
from django.db import transaction
from seloing.models import Seloing
from stats.models import UserStats, GlobalStats
from seloing.utils import update_seloing_statistics


class Command(BaseCommand):
    help = '기존에 완료된 셀로잉들의 통계를 일괄 업데이트합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='모든 통계를 초기화하고 다시 계산합니다.',
        )

    def handle(self, *args, **options):
        self.stdout.write('기존 완료된 셀로잉들의 통계 업데이트를 시작합니다...\n')

        # 완료된 셀로잉들 조회
        completed_seloings = Seloing.objects.filter(
            is_completed=True,
            seloingresult__isnull=False
        ).select_related('user', 'seloingresult')

        if not completed_seloings.exists():
            self.stdout.write(self.style.WARNING('완료된 셀로잉이 없습니다.'))
            return

        self.stdout.write(f'총 {completed_seloings.count()}개의 완료된 셀로잉을 찾았습니다.')

        # 통계 초기화 옵션
        if options['reset']:
            self.stdout.write('모든 통계를 초기화합니다...')
            with transaction.atomic():
                UserStats.objects.all().update(
                    total_seloing_count=0,
                    total_seloing_score=0,
                    total_repeat_score=0,
                    total_stable_score=0,
                    total_topic_score=0,
                    total_filler_score=0,
                    total_repeat_count=0,
                    total_filler_count=0,
                )
                GlobalStats.objects.all().update(
                    global_seloing_count=0,
                    global_seloing_score=0,
                    global_repeat_score=0,
                    global_stable_score=0,
                    global_topic_score=0,
                    global_filler_score=0,
                    global_repeat_count=0,
                    global_filler_count=0,
                )
            self.stdout.write(self.style.SUCCESS('통계 초기화 완료'))

        # 유저별로 셀로잉을 그룹화하여 순서대로 처리
        users_with_seloings = {}
        for seloing in completed_seloings.order_by('user', 'created_at'):
            if seloing.user not in users_with_seloings:
                users_with_seloings[seloing.user] = []
            users_with_seloings[seloing.user].append(seloing)

        updated_count = 0
        global_updates = 0

        with transaction.atomic():
            for user, user_seloings in users_with_seloings.items():
                self.stdout.write(f'\n{user.username} 유저의 {len(user_seloings)}개 셀로잉 처리 중...')
                
                # 통계 초기화를 안했다면 기존 통계를 가져와서 초기화
                if not options['reset']:
                    user_stats, created = UserStats.objects.get_or_create(user=user)
                    user_stats.total_seloing_count = 0
                    user_stats.total_seloing_score = 0
                    user_stats.total_repeat_score = 0
                    user_stats.total_stable_score = 0
                    user_stats.total_topic_score = 0
                    user_stats.total_filler_score = 0
                    user_stats.total_repeat_count = 0
                    user_stats.total_filler_count = 0
                    user_stats.save()

                # 각 셀로잉을 순서대로 처리
                for seloing in user_seloings:
                    # 통계 업데이트 (기존 utils 함수 사용하지 않고 직접 처리)
                    user_stats, created = UserStats.objects.get_or_create(user=user)
                    
                    user_stats.total_seloing_count += 1
                    user_stats.total_seloing_score += seloing.seloingresult.total_score
                    user_stats.total_repeat_score += seloing.seloingresult.repeat_score
                    user_stats.total_stable_score += seloing.seloingresult.stability_score
                    user_stats.total_topic_score += seloing.seloingresult.topic_score
                    user_stats.total_filler_score += seloing.seloingresult.filler_score
                    user_stats.total_repeat_count += seloing.seloingresult.repeat_count
                    user_stats.total_filler_count += seloing.seloingresult.filler_count
                    user_stats.save()

                    updated_count += 1

                    # 글로벌 통계 업데이트 (3회 이상일 때만)
                    if user_stats.total_seloing_count >= 3:
                        global_stats, created = GlobalStats.objects.get_or_create(id=1)
                        global_stats.global_seloing_count += 1
                        global_stats.global_seloing_score += seloing.seloingresult.total_score
                        global_stats.global_repeat_score += seloing.seloingresult.repeat_score
                        global_stats.global_stable_score += seloing.seloingresult.stability_score
                        global_stats.global_topic_score += seloing.seloingresult.topic_score
                        global_stats.global_filler_score += seloing.seloingresult.filler_score
                        global_stats.global_repeat_count += seloing.seloingresult.repeat_count
                        global_stats.global_filler_count += seloing.seloingresult.filler_count
                        global_stats.save()
                        global_updates += 1

                # 유저 통계 최종 확인
                user_stats.refresh_from_db()
                self.stdout.write(
                    f'  ✓ {user.username}: 총 {user_stats.total_seloing_count}회, '
                    f'평균 {user_stats.total_seloing_score_avg:.1f}점'
                )

        # 최종 결과 출력
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'통계 업데이트 완료!'))
        self.stdout.write(f'  - 처리된 셀로잉: {updated_count}개')
        self.stdout.write(f'  - 글로벌 통계에 포함된 셀로잉: {global_updates}개')
        self.stdout.write(f'  - 영향받은 유저: {len(users_with_seloings)}명')

        # 글로벌 통계 최종 확인
        global_stats = GlobalStats.objects.get(id=1)
        self.stdout.write(f'  - 글로벌 총 셀로잉 수: {global_stats.global_seloing_count}')
        self.stdout.write(f'  - 글로벌 총점: {global_stats.global_seloing_score}')
        if global_stats.global_seloing_count > 0:
            avg = global_stats.global_seloing_score / global_stats.global_seloing_count
            self.stdout.write(f'  - 글로벌 평균: {avg:.1f}점')