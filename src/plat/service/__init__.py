from datetime import timedelta

from plat.repository.d_basic import SimpleKVRepository
from plat.service.acc_service import AccountService
from plat.service.info_service import PersonalInfoService, PublicInfoService
from xtu_ems.ems.handler.get_classroom_status import TodayClassroomStatusGetter, TomorrowClassroomStatusGetter
from xtu_ems.ems.handler.get_student_courses import StudentCourseGetter
from xtu_ems.ems.handler.get_student_exam import StudentExamGetter
from xtu_ems.ems.handler.get_student_info import StudentInfoGetter
from xtu_ems.ems.handler.get_students_transcript import StudentTranscriptGetter
from xtu_ems.ems.handler.get_teaching_calendar import TeachingCalendarGetter

account_repository = SimpleKVRepository()

info_service = PersonalInfoService(handler=StudentInfoGetter(),
                                   update_expire=timedelta(days=1),
                                   submit_expire=timedelta(minutes=3),
                                   account_repository=account_repository
                                   )

score_service = PersonalInfoService(handler=StudentTranscriptGetter(),
                                    update_expire=timedelta(days=1),
                                    submit_expire=timedelta(minutes=15),
                                    account_repository=account_repository
                                    )

course_service = PersonalInfoService(handler=StudentCourseGetter(),
                                     update_expire=timedelta(days=1),
                                     submit_expire=timedelta(minutes=20),
                                     account_repository=account_repository
                                     )

exam_service = PersonalInfoService(handler=StudentExamGetter(),
                                   update_expire=timedelta(days=1),
                                   submit_expire=timedelta(minutes=20),
                                   account_repository=account_repository
                                   )

rank_service = PersonalInfoService(handler=StudentTranscriptGetter(),
                                   update_expire=timedelta(days=1),
                                   submit_expire=timedelta(minutes=15),
                                   account_repository=account_repository
                                   )

calendar_service = PublicInfoService(handler=TeachingCalendarGetter(),
                                     update_expire=timedelta(days=30),
                                     submit_expire=timedelta(minutes=15),
                                     account_repository=account_repository
                                     )

today_classroom_service = PublicInfoService(handler=TodayClassroomStatusGetter(),
                                            update_expire=timedelta(hours=12),
                                            submit_expire=timedelta(minutes=15),
                                            account_repository=account_repository
                                            )
tomorrow_classroom_service = PublicInfoService(handler=TomorrowClassroomStatusGetter(),
                                               update_expire=timedelta(hours=12),
                                               submit_expire=timedelta(minutes=15),
                                               account_repository=account_repository
                                               )

account_service = AccountService(account_repository=account_repository)
