package main

import (
	"cached_proxy/icalendar"
	"os"
	"time"
)

// SpiderUrl 爬虫地址
var (
	SpiderUrl = os.Getenv("SPIDER_URL")
)

// 日历事件的默认提醒
var (
	// DefaultCourseAlarms 课程事件的默认提醒
	DefaultCourseAlarms = []icalendar.Alarm{
		icalendar.NewIcsAlarm("DISPLAY", 30*time.Minute, "距离上课仅剩30分钟"),
	}
	// DefaultExamAlarms 考试事件的默认提醒
	DefaultExamAlarms = []icalendar.Alarm{
		icalendar.NewIcsAlarm("DISPLAY", 30*time.Minute, "距离考试仅剩30分钟")
	}
)

// 日历事件的标题和描述的配置
const (
	ExamSummaryPrefix       = "【考试】"
	ExamDescSuffix          = "【拱拱】"
	CourseSummaryPrefix     = "【课程】"
	CourseDescSummarySuffix = "【拱拱】"
	ProdID                  = "-//sky31studio//GongGong//CN"
)

const (
	ApiPort = 8080
)
