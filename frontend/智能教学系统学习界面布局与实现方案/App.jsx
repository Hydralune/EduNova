import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { 
  BookOpen, 
  Clock, 
  CheckCircle, 
  PlayCircle, 
  MessageCircle, 
  FileText, 
  Star,
  ChevronRight,
  ChevronDown,
  Settings,
  User,
  Brain,
  Target,
  Award,
  Bookmark,
  Volume2,
  Sun,
  Moon,
  Maximize,
  RotateCcw,
  Share2,
  TrendingUp,
  Calendar,
  Bell,
  Search
} from 'lucide-react'
import AIChat from './components/AIChat.jsx'
import QuizSystem from './components/QuizSystem.jsx'
import './App.css'

function App() {
  const [currentChapter, setCurrentChapter] = useState(1)
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [expandedChapters, setExpandedChapters] = useState([1])
  const [learningProgress, setLearningProgress] = useState(65)
  const [showAIChat, setShowAIChat] = useState(false)
  const [showQuiz, setShowQuiz] = useState(false)
  const [readingProgress, setReadingProgress] = useState(0)
  const [isChatMinimized, setIsChatMinimized] = useState(false)
  const [studyTime, setStudyTime] = useState(0)
  const [notifications, setNotifications] = useState([
    { id: 1, message: "新的练习题已发布", time: "5分钟前", type: "info" },
    { id: 2, message: "恭喜完成第2章学习", time: "1小时前", type: "success" }
  ])

  // 模拟课程数据
  const courseData = {
    title: "前端开发基础",
    description: "从零开始学习现代前端开发技术",
    totalChapters: 8,
    completedChapters: 5,
    instructor: "张老师",
    rating: 4.8,
    students: 1234,
    chapters: [
      {
        id: 1,
        title: "HTML基础",
        sections: ["HTML简介", "标签和属性", "表单元素", "语义化标签"],
        completed: true,
        duration: "2小时",
        progress: 100
      },
      {
        id: 2,
        title: "CSS样式",
        sections: ["CSS选择器", "盒模型", "布局技术", "响应式设计"],
        completed: true,
        duration: "3小时",
        progress: 100
      },
      {
        id: 3,
        title: "JavaScript基础",
        sections: ["变量和数据类型", "函数", "DOM操作", "事件处理"],
        completed: false,
        duration: "4小时",
        current: true,
        progress: 75
      },
      {
        id: 4,
        title: "React入门",
        sections: ["组件概念", "JSX语法", "状态管理", "生命周期"],
        completed: false,
        duration: "5小时",
        progress: 0
      },
      {
        id: 5,
        title: "项目实战",
        sections: ["项目规划", "组件开发", "状态管理", "部署上线"],
        completed: false,
        duration: "8小时",
        progress: 0
      }
    ]
  }

  // 当前学习内容
  const currentContent = {
    title: "JavaScript变量和数据类型",
    content: `
# JavaScript变量和数据类型

JavaScript是一种动态类型语言，这意味着变量可以存储不同类型的数据。

## 变量声明

在JavaScript中，有三种声明变量的方式：

### 1. var
\`\`\`javascript
var name = "张三";
var age = 25;
\`\`\`

### 2. let
\`\`\`javascript
let name = "李四";
let age = 30;
\`\`\`

### 3. const
\`\`\`javascript
const PI = 3.14159;
const companyName = "科技公司";
\`\`\`

## 数据类型

JavaScript有以下基本数据类型：

- **String（字符串）**: 文本数据
- **Number（数字）**: 数值数据
- **Boolean（布尔）**: true或false
- **Undefined**: 未定义的值
- **Null**: 空值
- **Symbol**: 唯一标识符
- **BigInt**: 大整数

### 示例代码

\`\`\`javascript
// 字符串
let message = "Hello, World!";

// 数字
let count = 42;
let price = 19.99;

// 布尔值
let isActive = true;
let isComplete = false;

// 数组
let colors = ["红色", "绿色", "蓝色"];

// 对象
let person = {
  name: "王五",
  age: 28,
  city: "北京"
};
\`\`\`

## 类型检测

使用 \`typeof\` 操作符可以检测变量的类型：

\`\`\`javascript
console.log(typeof "Hello"); // "string"
console.log(typeof 42); // "number"
console.log(typeof true); // "boolean"
\`\`\`

## 练习题

1. 声明一个变量存储你的姓名
2. 创建一个对象包含学生信息
3. 使用typeof检测不同变量的类型

## 小结

理解JavaScript的变量声明和数据类型是编程的基础。记住：
- 使用const声明常量
- 使用let声明变量
- 避免使用var（除非必要）
- 使用typeof检测数据类型
    `,
    estimatedTime: "15分钟",
    difficulty: "初级",
    lastUpdated: "2024-01-15"
  }

  // 学习统计数据
  const learningStats = {
    totalTime: "24小时",
    completedLessons: 12,
    currentStreak: 7,
    weeklyGoal: 10,
    weeklyProgress: 7
  }

  // 模拟滚动进度
  useEffect(() => {
    const handleScroll = () => {
      const scrolled = window.scrollY
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight
      const progress = maxScroll > 0 ? (scrolled / maxScroll) * 100 : 0
      setReadingProgress(Math.min(progress, 100))
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // 学习时间计时器
  useEffect(() => {
    const timer = setInterval(() => {
      setStudyTime(prev => prev + 1)
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const formatStudyTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const toggleChapter = (chapterId) => {
    setExpandedChapters(prev => 
      prev.includes(chapterId) 
        ? prev.filter(id => id !== chapterId)
        : [...prev, chapterId]
    )
  }

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode)
    document.documentElement.classList.toggle('dark')
  }

  const handleChapterSelect = (chapterId) => {
    setCurrentChapter(chapterId)
    // 这里可以加载对应章节的内容
  }

  return (
    <div className={`min-h-screen bg-background ${isDarkMode ? 'dark' : ''}`}>
      {/* 顶部导航栏 */}
      <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-primary" />
              <h1 className="text-xl font-bold">智能教学系统</h1>
            </div>
            <Badge variant="secondary">学生模式</Badge>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="hidden md:flex items-center space-x-4 text-sm text-muted-foreground">
              <div className="flex items-center space-x-1">
                <Clock className="h-4 w-4" />
                <span>学习时长: {formatStudyTime(studyTime)}</span>
              </div>
              <div className="flex items-center space-x-1">
                <TrendingUp className="h-4 w-4" />
                <span>连续学习: {learningStats.currentStreak}天</span>
              </div>
            </div>
            
            <Button variant="ghost" size="sm">
              <Search className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="h-4 w-4" />
              {notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full text-xs"></span>
              )}
            </Button>
            <Button variant="ghost" size="sm" onClick={toggleDarkMode}>
              {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm">
              <User className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* 阅读进度条 */}
        <div className="w-full h-1 bg-muted">
          <div 
            className="h-full bg-primary transition-all duration-300"
            style={{ width: `${readingProgress}%` }}
          />
        </div>
      </header>

      <div className="flex">
        {/* 侧边栏 */}
        <aside className="w-80 min-h-screen border-r bg-card">
          <div className="p-6">
            {/* 课程信息 */}
            <div className="mb-6">
              <div className="flex items-center space-x-2 mb-2">
                <h2 className="text-lg font-semibold">{courseData.title}</h2>
                <div className="flex items-center space-x-1">
                  <Star className="h-4 w-4 text-yellow-500 fill-current" />
                  <span className="text-sm text-muted-foreground">{courseData.rating}</span>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mb-2">{courseData.description}</p>
              <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                <span>讲师: {courseData.instructor}</span>
                <span>{courseData.students} 学生</span>
              </div>
              
              {/* 总体进度 */}
              <div className="mt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span>学习进度</span>
                  <span>{learningProgress}%</span>
                </div>
                <Progress value={learningProgress} className="h-2" />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{courseData.completedChapters}/{courseData.totalChapters} 章节完成</span>
                  <span>还需 2小时</span>
                </div>
              </div>
            </div>

            {/* 学习统计 */}
            <div className="mb-6 p-4 bg-muted/50 rounded-lg">
              <h3 className="text-sm font-medium mb-3">学习统计</h3>
              <div className="grid grid-cols-2 gap-3 text-center">
                <div>
                  <div className="text-lg font-bold text-primary">{learningStats.totalTime}</div>
                  <div className="text-xs text-muted-foreground">总学习时长</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-green-600">{learningStats.completedLessons}</div>
                  <div className="text-xs text-muted-foreground">完成课程</div>
                </div>
              </div>
              <div className="mt-3">
                <div className="flex justify-between text-xs mb-1">
                  <span>本周目标</span>
                  <span>{learningStats.weeklyProgress}/{learningStats.weeklyGoal}</span>
                </div>
                <Progress value={(learningStats.weeklyProgress / learningStats.weeklyGoal) * 100} className="h-1" />
              </div>
            </div>

            {/* 快速操作 */}
            <div className="mb-6">
              <h3 className="text-sm font-medium mb-3">快速操作</h3>
              <div className="grid grid-cols-2 gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="justify-start"
                  onClick={() => setShowAIChat(true)}
                >
                  <MessageCircle className="h-4 w-4 mr-2" />
                  AI助手
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="justify-start"
                  onClick={() => setShowQuiz(true)}
                >
                  <Target className="h-4 w-4 mr-2" />
                  练习
                </Button>
                <Button variant="outline" size="sm" className="justify-start">
                  <FileText className="h-4 w-4 mr-2" />
                  笔记
                </Button>
                <Button variant="outline" size="sm" className="justify-start">
                  <Bookmark className="h-4 w-4 mr-2" />
                  收藏
                </Button>
              </div>
            </div>

            {/* 章节导航 */}
            <div>
              <h3 className="text-sm font-medium mb-3">课程章节</h3>
              <ScrollArea className="h-96">
                <div className="space-y-2">
                  {courseData.chapters.map((chapter) => (
                    <div key={chapter.id} className="space-y-2">
                      <div 
                        className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                          chapter.current ? 'bg-primary/10 border border-primary/20' : 'hover:bg-muted'
                        }`}
                        onClick={() => {
                          toggleChapter(chapter.id)
                          handleChapterSelect(chapter.id)
                        }}
                      >
                        <div className="flex items-center space-x-3 flex-1">
                          {chapter.completed ? (
                            <CheckCircle className="h-5 w-5 text-green-500" />
                          ) : chapter.current ? (
                            <PlayCircle className="h-5 w-5 text-primary" />
                          ) : (
                            <div className="h-5 w-5 rounded-full border-2 border-muted-foreground" />
                          )}
                          <div className="flex-1">
                            <div className="font-medium text-sm">{chapter.title}</div>
                            <div className="text-xs text-muted-foreground flex items-center justify-between">
                              <div className="flex items-center">
                                <Clock className="h-3 w-3 mr-1" />
                                {chapter.duration}
                              </div>
                              <span>{chapter.progress}%</span>
                            </div>
                            {chapter.progress > 0 && chapter.progress < 100 && (
                              <Progress value={chapter.progress} className="h-1 mt-1" />
                            )}
                          </div>
                        </div>
                        {expandedChapters.includes(chapter.id) ? (
                          <ChevronDown className="h-4 w-4" />
                        ) : (
                          <ChevronRight className="h-4 w-4" />
                        )}
                      </div>
                      
                      {/* 章节内容 */}
                      {expandedChapters.includes(chapter.id) && (
                        <div className="ml-8 space-y-1">
                          {chapter.sections.map((section, index) => (
                            <div 
                              key={index}
                              className="text-sm text-muted-foreground hover:text-foreground cursor-pointer py-1 px-2 rounded hover:bg-muted flex items-center justify-between"
                            >
                              <span>{section}</span>
                              {chapter.completed && <CheckCircle className="h-3 w-3 text-green-500" />}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          </div>
        </aside>

        {/* 主内容区域 */}
        <main className="flex-1 min-h-screen">
          <div className="container max-w-4xl mx-auto p-6">
            {/* 内容头部 */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h1 className="text-2xl font-bold mb-2">{currentContent.title}</h1>
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      预计 {currentContent.estimatedTime}
                    </div>
                    <Badge variant="outline">{currentContent.difficulty}</Badge>
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-1" />
                      更新于 {currentContent.lastUpdated}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm" title="朗读">
                    <Volume2 className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" title="全屏">
                    <Maximize className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" title="分享">
                    <Share2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* 学习内容 */}
            <Card className="mb-6">
              <CardContent className="p-8">
                <div className="prose prose-slate dark:prose-invert max-w-none">
                  <div dangerouslySetInnerHTML={{ 
                    __html: currentContent.content
                      .replace(/\n/g, '<br>')
                      .replace(/```javascript\n([\s\S]*?)\n```/g, '<pre class="bg-muted p-4 rounded-lg overflow-x-auto my-4"><code class="language-javascript">$1</code></pre>')
                      .replace(/`([^`]+)`/g, '<code class="bg-muted px-2 py-1 rounded text-sm">$1</code>')
                      .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold mt-6 mb-3">$1</h3>')
                      .replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mt-8 mb-4">$1</h2>')
                      .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-8 mb-6">$1</h1>')
                      .replace(/^\- (.*$)/gm, '<li class="ml-4 mb-1">$1</li>')
                      .replace(/^\d+\. (.*$)/gm, '<li class="ml-4 mb-1">$1</li>')
                  }} />
                </div>
              </CardContent>
            </Card>

            {/* 学习进度提示 */}
            <Card className="mb-6 border-l-4 border-l-primary">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">学习进度</h3>
                    <p className="text-sm text-muted-foreground">
                      你已经完成了本章节的 75%，继续加油！
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary">75%</div>
                    <div className="text-xs text-muted-foreground">3/4 小节</div>
                  </div>
                </div>
                <Progress value={75} className="mt-3" />
              </CardContent>
            </Card>

            {/* 底部操作栏 */}
            <div className="flex items-center justify-between p-4 bg-card rounded-lg border">
              <div className="flex items-center space-x-4">
                <Button variant="outline">
                  <RotateCcw className="h-4 w-4 mr-2" />
                  重新学习
                </Button>
                <Button variant="outline">
                  <FileText className="h-4 w-4 mr-2" />
                  做笔记
                </Button>
                <Button variant="outline">
                  <Bookmark className="h-4 w-4 mr-2" />
                  收藏本节
                </Button>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button variant="outline">上一节</Button>
                <Button 
                  onClick={() => setShowQuiz(true)}
                  className="bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  开始练习
                  <ChevronRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* AI聊天组件 */}
      <AIChat
        isOpen={showAIChat}
        onClose={() => setShowAIChat(false)}
        onMinimize={() => setIsChatMinimized(!isChatMinimized)}
        isMinimized={isChatMinimized}
        currentTopic="JavaScript基础"
      />

      {/* 测验组件 */}
      <QuizSystem
        isOpen={showQuiz}
        onClose={() => setShowQuiz(false)}
        currentTopic="JavaScript基础"
      />
    </div>
  )
}

export default App

