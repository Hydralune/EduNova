import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Bookmark,
  BookmarkCheck,
  RotateCcw,
  Eye,
  EyeOff,
  Target,
  Award,
  TrendingUp,
  X,
  ChevronLeft,
  ChevronRight,
  Flag
} from 'lucide-react'

const QuizSystem = ({ isOpen, onClose, currentTopic = "JavaScript基础" }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [bookmarkedQuestions, setBookmarkedQuestions] = useState(new Set())
  const [timeRemaining, setTimeRemaining] = useState(300) // 5分钟
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [showExplanation, setShowExplanation] = useState(false)
  const [quizStarted, setQuizStarted] = useState(false)

  // 模拟题目数据
  const questions = [
    {
      id: 1,
      question: "下列哪种方式可以声明一个常量？",
      options: [
        "var PI = 3.14",
        "let PI = 3.14", 
        "const PI = 3.14",
        "define PI = 3.14"
      ],
      correctAnswer: 2,
      explanation: "const关键字用于声明常量，一旦赋值后不能再修改。var和let声明的是变量，define不是JavaScript的关键字。",
      difficulty: "初级",
      topic: "变量声明"
    },
    {
      id: 2,
      question: "JavaScript中哪个操作符可以检测变量的数据类型？",
      options: [
        "instanceof",
        "typeof",
        "type",
        "check"
      ],
      correctAnswer: 1,
      explanation: "typeof操作符返回一个字符串，表示未经计算的操作数的类型。例如：typeof 'hello' 返回 'string'。",
      difficulty: "初级",
      topic: "数据类型"
    },
    {
      id: 3,
      question: "以下哪个不是JavaScript的基本数据类型？",
      options: [
        "String",
        "Number",
        "Array",
        "Boolean"
      ],
      correctAnswer: 2,
      explanation: "Array是引用数据类型，不是基本数据类型。JavaScript的基本数据类型包括：String、Number、Boolean、Undefined、Null、Symbol、BigInt。",
      difficulty: "中级",
      topic: "数据类型"
    },
    {
      id: 4,
      question: "下列关于变量作用域的说法，哪个是正确的？",
      options: [
        "var声明的变量具有块级作用域",
        "let声明的变量具有函数作用域",
        "const声明的变量具有块级作用域",
        "所有变量都具有全局作用域"
      ],
      correctAnswer: 2,
      explanation: "const和let都具有块级作用域，只在声明它们的代码块内有效。var具有函数作用域或全局作用域。",
      difficulty: "中级",
      topic: "作用域"
    },
    {
      id: 5,
      question: "以下代码的输出结果是什么？\n\nconsole.log(typeof null);",
      options: [
        "'null'",
        "'undefined'",
        "'object'",
        "'boolean'"
      ],
      correctAnswer: 2,
      explanation: "这是JavaScript的一个历史遗留问题。typeof null 返回 'object'，尽管null不是对象。这被认为是语言设计的一个错误。",
      difficulty: "高级",
      topic: "特殊情况"
    }
  ]

  const currentQuestion = questions[currentQuestionIndex]
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100

  // 计时器
  useEffect(() => {
    if (!quizStarted || isSubmitted) return

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          handleSubmitQuiz()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [quizStarted, isSubmitted])

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const handleAnswerSelect = (optionIndex) => {
    setAnswers(prev => ({
      ...prev,
      [currentQuestion.id]: optionIndex
    }))
  }

  const handleBookmark = (questionId) => {
    setBookmarkedQuestions(prev => {
      const newSet = new Set(prev)
      if (newSet.has(questionId)) {
        newSet.delete(questionId)
      } else {
        newSet.add(questionId)
      }
      return newSet
    })
  }

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
      setShowExplanation(false)
    }
  }

  const handlePrevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1)
      setShowExplanation(false)
    }
  }

  const handleSubmitQuiz = () => {
    setIsSubmitted(true)
    setQuizStarted(false)
  }

  const calculateScore = () => {
    let correct = 0
    questions.forEach(question => {
      if (answers[question.id] === question.correctAnswer) {
        correct++
      }
    })
    return {
      correct,
      total: questions.length,
      percentage: Math.round((correct / questions.length) * 100)
    }
  }

  const getQuestionStatus = (questionId) => {
    if (answers[questionId] !== undefined) {
      if (isSubmitted) {
        const question = questions.find(q => q.id === questionId)
        return answers[questionId] === question.correctAnswer ? 'correct' : 'incorrect'
      }
      return 'answered'
    }
    return 'unanswered'
  }

  const startQuiz = () => {
    setQuizStarted(true)
    setCurrentQuestionIndex(0)
    setAnswers({})
    setIsSubmitted(false)
    setTimeRemaining(300)
  }

  const restartQuiz = () => {
    setQuizStarted(false)
    setCurrentQuestionIndex(0)
    setAnswers({})
    setIsSubmitted(false)
    setTimeRemaining(300)
    setBookmarkedQuestions(new Set())
  }

  if (!isOpen) return null

  // 开始界面
  if (!quizStarted && !isSubmitted) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="flex items-center justify-between mb-4">
              <CardTitle className="text-xl">{currentTopic} 测验</CardTitle>
              <Button variant="ghost" size="sm" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-center w-16 h-16 mx-auto bg-primary/10 rounded-full">
                <Target className="h-8 w-8 text-primary" />
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-semibold">准备开始测验</h3>
                <p className="text-sm text-muted-foreground">
                  本次测验包含 {questions.length} 道题目，限时 5 分钟
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="text-center p-3 bg-muted rounded-lg">
                <div className="font-semibold">{questions.length}</div>
                <div className="text-muted-foreground">题目数量</div>
              </div>
              <div className="text-center p-3 bg-muted rounded-lg">
                <div className="font-semibold">5 分钟</div>
                <div className="text-muted-foreground">答题时间</div>
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">测验说明：</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• 每题只能选择一个答案</li>
                <li>• 可以标记题目稍后回顾</li>
                <li>• 时间到自动提交</li>
                <li>• 提交后可查看详细解析</li>
              </ul>
            </div>
            <Button onClick={startQuiz} className="w-full">
              开始测验
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // 结果界面
  if (isSubmitted) {
    const score = calculateScore()
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <Card className="w-full max-w-2xl">
          <CardHeader className="text-center">
            <div className="flex items-center justify-between mb-4">
              <CardTitle className="text-xl">测验完成</CardTitle>
              <Button variant="ghost" size="sm" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-center w-20 h-20 mx-auto bg-primary/10 rounded-full">
                <Award className="h-10 w-10 text-primary" />
              </div>
              <div>
                <div className="text-3xl font-bold text-primary">{score.percentage}%</div>
                <div className="text-muted-foreground">
                  {score.correct} / {score.total} 题正确
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* 成绩分析 */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{score.correct}</div>
                <div className="text-sm text-green-600">正确</div>
              </div>
              <div className="p-3 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{score.total - score.correct}</div>
                <div className="text-sm text-red-600">错误</div>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{bookmarkedQuestions.size}</div>
                <div className="text-sm text-blue-600">标记</div>
              </div>
            </div>

            {/* 题目回顾 */}
            <div>
              <h3 className="font-semibold mb-3">题目回顾</h3>
              <ScrollArea className="h-48">
                <div className="space-y-2">
                  {questions.map((question, index) => {
                    const status = getQuestionStatus(question.id)
                    const isBookmarked = bookmarkedQuestions.has(question.id)
                    
                    return (
                      <div 
                        key={question.id}
                        className="flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:bg-muted"
                        onClick={() => {
                          setCurrentQuestionIndex(index)
                          setShowExplanation(true)
                        }}
                      >
                        <div className="flex items-center space-x-3">
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium">第 {index + 1} 题</span>
                            {status === 'correct' && <CheckCircle className="h-4 w-4 text-green-500" />}
                            {status === 'incorrect' && <XCircle className="h-4 w-4 text-red-500" />}
                            {isBookmarked && <BookmarkCheck className="h-4 w-4 text-blue-500" />}
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {question.difficulty}
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {question.topic}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </ScrollArea>
            </div>

            <div className="flex space-x-2">
              <Button onClick={restartQuiz} variant="outline" className="flex-1">
                <RotateCcw className="h-4 w-4 mr-2" />
                重新测验
              </Button>
              <Button onClick={onClose} className="flex-1">
                完成
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // 答题界面
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-4xl h-[600px] flex flex-col">
        <CardHeader className="flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <CardTitle className="text-lg">{currentTopic} 测验</CardTitle>
              <Badge variant="outline">{currentQuestion.difficulty}</Badge>
              <Badge variant="secondary">{currentQuestion.topic}</Badge>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>第 {currentQuestionIndex + 1} 题 / 共 {questions.length} 题</span>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1">
                <Clock className="h-4 w-4" />
                <span className={timeRemaining < 60 ? 'text-red-500 font-semibold' : ''}>
                  剩余时间: {formatTime(timeRemaining)}
                </span>
              </div>
            </div>
          </div>
          
          <Progress value={progress} className="h-2" />
        </CardHeader>

        <CardContent className="flex-1 flex flex-col">
          <div className="flex-1">
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-4 leading-relaxed">
                {currentQuestion.question}
              </h3>
              
              <div className="space-y-3">
                {currentQuestion.options.map((option, index) => {
                  const isSelected = answers[currentQuestion.id] === index
                  const isCorrect = index === currentQuestion.correctAnswer
                  const isIncorrect = isSubmitted && isSelected && !isCorrect
                  
                  return (
                    <label 
                      key={index}
                      className={`flex items-center space-x-3 p-4 border rounded-lg cursor-pointer transition-colors ${
                        isSelected ? 'border-primary bg-primary/5' : 'hover:bg-muted'
                      } ${
                        isSubmitted && isCorrect ? 'border-green-500 bg-green-50' : ''
                      } ${
                        isIncorrect ? 'border-red-500 bg-red-50' : ''
                      }`}
                      onClick={() => !isSubmitted && handleAnswerSelect(index)}
                    >
                      <input 
                        type="radio" 
                        name={`question-${currentQuestion.id}`}
                        checked={isSelected}
                        onChange={() => {}}
                        className="text-primary"
                        disabled={isSubmitted}
                      />
                      <span className="flex-1">
                        {String.fromCharCode(65 + index)}. {option}
                      </span>
                      {isSubmitted && isCorrect && <CheckCircle className="h-5 w-5 text-green-500" />}
                      {isIncorrect && <XCircle className="h-5 w-5 text-red-500" />}
                    </label>
                  )
                })}
              </div>
            </div>

            {/* 解析 */}
            {showExplanation && (
              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-2 mb-2">
                  <AlertCircle className="h-5 w-5 text-blue-600" />
                  <span className="font-medium text-blue-900">题目解析</span>
                </div>
                <p className="text-sm text-blue-800">{currentQuestion.explanation}</p>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between pt-4 border-t">
            <div className="flex items-center space-x-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => handleBookmark(currentQuestion.id)}
              >
                {bookmarkedQuestions.has(currentQuestion.id) ? (
                  <BookmarkCheck className="h-4 w-4 mr-2 text-blue-500" />
                ) : (
                  <Bookmark className="h-4 w-4 mr-2" />
                )}
                标记题目
              </Button>
              
              {isSubmitted && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setShowExplanation(!showExplanation)}
                >
                  {showExplanation ? (
                    <EyeOff className="h-4 w-4 mr-2" />
                  ) : (
                    <Eye className="h-4 w-4 mr-2" />
                  )}
                  {showExplanation ? '隐藏解析' : '查看解析'}
                </Button>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <Button 
                variant="outline" 
                onClick={handlePrevQuestion}
                disabled={currentQuestionIndex === 0}
              >
                <ChevronLeft className="h-4 w-4 mr-2" />
                上一题
              </Button>
              
              {currentQuestionIndex === questions.length - 1 ? (
                <Button 
                  onClick={handleSubmitQuiz}
                  disabled={Object.keys(answers).length === 0}
                >
                  <Flag className="h-4 w-4 mr-2" />
                  提交答案
                </Button>
              ) : (
                <Button onClick={handleNextQuestion}>
                  下一题
                  <ChevronRight className="h-4 w-4 ml-2" />
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default QuizSystem

