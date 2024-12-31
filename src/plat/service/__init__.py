from plat.config import CACHE_CONFIG
from plat.repository.d_basic import SimpleKVRepository
from plat.service.acc_service import AccountService
from plat.service.info_service import PersonalInfoService, PublicInfoService
from xtu_ems.ems.handler.get_classroom_status import TodayClassroomStatusGetter, TomorrowClassroomStatusGetter
from xtu_ems.ems.handler.get_student_courses import StudentCourseGetter
from xtu_ems.ems.handler.get_student_exam import StudentExamGetter
from xtu_ems.ems.handler.get_student_info import StudentInfoGetter
from xtu_ems.ems.handler.get_students_transcript import StudentTranscriptGetter, StudentRankGetter, \
    StudentTranscriptGetterForAcademicMinor
from xtu_ems.ems.handler.get_teaching_calendar import TeachingCalendarGetter

account_repository = SimpleKVRepository()

info_service = PersonalInfoService(handler=StudentInfoGetter(),
                                   update_expire=CACHE_CONFIG.PERSONAL_INFO_UPDATE,
                                   submit_expire=CACHE_CONFIG.PERSONAL_INFO_SUBMIT,
                                   account_repository=account_repository
                                   )

score_service = PersonalInfoService(handler=StudentTranscriptGetter(),
                                    update_expire=CACHE_CONFIG.SCORE_UPDATE,
                                    submit_expire=CACHE_CONFIG.SCORE_SUBMIT,
                                    account_repository=account_repository
                                    )

minor_score_service = PersonalInfoService(handler=StudentTranscriptGetterForAcademicMinor(),
                                          update_expire=CACHE_CONFIG.MINOR_SCORE_UPDATE,
                                          submit_expire=CACHE_CONFIG.MINOR_SCORE_SUBMIT,
                                          account_repository=account_repository
                                          )

course_service = PersonalInfoService(handler=StudentCourseGetter(),
                                     update_expire=CACHE_CONFIG.COURSE_UPDATE,
                                     submit_expire=CACHE_CONFIG.COURSE_SUBMIT,
                                     account_repository=account_repository
                                     )

exam_service = PersonalInfoService(handler=StudentExamGetter(),
                                   update_expire=CACHE_CONFIG.EXAM_UPDATE,
                                   submit_expire=CACHE_CONFIG.EXAM_SUBMIT,
                                   account_repository=account_repository
                                   )

rank_service = PersonalInfoService(handler=StudentRankGetter(),
                                   update_expire=CACHE_CONFIG.RANK_UPDATE,
                                   submit_expire=CACHE_CONFIG.RANK_SUBMIT,
                                   account_repository=account_repository
                                   )

calendar_service = PublicInfoService(handler=TeachingCalendarGetter(),
                                     update_expire=CACHE_CONFIG.CALENDAR_UPDATE,
                                     submit_expire=CACHE_CONFIG.CALENDAR_SUBMIT,
                                     account_repository=account_repository
                                     )

today_classroom_service = PublicInfoService(handler=TodayClassroomStatusGetter(),
                                            update_expire=CACHE_CONFIG.TODAY_CLASSROOM_UPDATE,
                                            submit_expire=CACHE_CONFIG.TODAY_CLASSROOM_SUBMIT,
                                            account_repository=account_repository
                                            )
tomorrow_classroom_service = PublicInfoService(handler=TomorrowClassroomStatusGetter(),
                                               update_expire=CACHE_CONFIG.TOMORROW_CLASSROOM_UPDATE,
                                               submit_expire=CACHE_CONFIG.TOMORROW_CLASSROOM_SUBMIT,
                                               account_repository=account_repository
                                               )

account_service = AccountService(account_repository=account_repository)
