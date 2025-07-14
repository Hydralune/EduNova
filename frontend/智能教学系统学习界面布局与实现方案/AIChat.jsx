import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Lightbulb,
  BookOpen,
  HelpCircle,
  Minimize2,
  Maximize2,
  X,
  Mic,
  MicOff,
  Volume2,
  Copy,
  ThumbsUp,
  ThumbsDown
} from 'lucide-react'

const AIChat = ({ isOpen, onClose, onMinimize, isMinimized, currentTopic = "JavaScript基础" }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: `你好！我是你的AI学习助手。我可以帮你解答关于${currentTopic}的任何问题。有什么我可以帮助你的吗？`,
      timestamp: new Date(),
      suggestions: [
        "什么是变量作用域？",
        "如何理解闭包概念？",
        "解释一下this关键字",
        "数组和对象的区别"
      ]
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (message = inputValue) => {
    if (!message.trim()) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    // 模拟AI回复
    setTimeout(() => {
      const aiResponse = generateAIResponse(message)
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: aiResponse.content,
        timestamp: new Date(),
        suggestions: aiResponse.suggestions,
        codeExample: aiResponse.codeExample
      }
      setMessages(prev => [...prev, aiMessage])
      setIsTyping(false)
    }, 1500)
  }

  const generateAIResponse = (userMessage) => {
    const responses = {
      "变量作用域": {
        content: "变量作用域是指变量在程序中可以被访问的范围。JavaScript中有三种作用域：\n\n1. **全局作用域** - 在任何地方都可以访问\n2. **函数作用域** - 只在函数内部可以访问\n3. **块级作用域** - 只在代码块内部可以访问（let、const）",
        codeExample: `// 全局作用域
var globalVar = "我是全局变量";

function myFunction() {
  // 函数作用域
  var functionVar = "我是函数变量";
  
  if (true) {
    // 块级作用域
    let blockVar = "我是块级变量";
    const blockConst = "我是块级常量";
  }
}`,
        suggestions: ["什么是闭包？", "var和let的区别", "如何避免变量污染"]
      },
      "闭包": {
        content: "闭包是JavaScript中的一个重要概念。当一个函数能够访问并使用其外部作用域的变量时，就形成了闭包。即使外部函数已经执行完毕，内部函数仍然可以访问外部函数的变量。",
        codeExample: `function outer(x) {
  // 外部函数的变量
  return function inner(y) {
    // 内部函数可以访问外部函数的变量x
    return x + y;
  };
}

const addFive = outer(5);
console.log(addFive(3)); // 输出: 8`,
        suggestions: ["闭包的应用场景", "闭包会造成内存泄漏吗", "如何理解词法作用域"]
      },
      "this": {
        content: "this关键字在JavaScript中指向当前执行上下文的对象。它的值取决于函数的调用方式：\n\n1. **全局上下文** - 指向window对象\n2. **对象方法** - 指向调用该方法的对象\n3. **构造函数** - 指向新创建的实例\n4. **箭头函数** - 继承外层作用域的this",
        codeExample: `const obj = {
  name: 'Alice',
  greet: function() {
    console.log('Hello, ' + this.name);
  },
  greetArrow: () => {
    console.log('Hello, ' + this.name); // this不指向obj
  }
};

obj.greet(); // "Hello, Alice"`,
        suggestions: ["call、apply、bind的区别", "箭头函数的this", "严格模式下的this"]
      }
    }

    // 简单的关键词匹配
    for (const [key, response] of Object.entries(responses)) {
      if (userMessage.toLowerCase().includes(key.toLowerCase())) {
        return response
      }
    }

    return {
      content: `关于"${userMessage}"，这是一个很好的问题！让我为你详细解释一下。\n\n在JavaScript学习过程中，理解基础概念非常重要。建议你多练习编写代码，通过实践来加深理解。\n\n你还有其他问题吗？`,
      suggestions: ["给我一些练习题", "推荐学习资源", "下一步应该学什么"]
    }
  }

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion)
  }

  const handleVoiceInput = () => {
    setIsListening(!isListening)
    // 这里可以集成语音识别API
  }

  const copyMessage = (content) => {
    navigator.clipboard.writeText(content)
  }

  const rateMessage = (messageId, rating) => {
    // 这里可以发送评分到后端
    console.log(`Message ${messageId} rated: ${rating}`)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className={`transition-all duration-300 ${isMinimized ? 'w-80 h-16' : 'w-[600px] h-[500px]'} flex flex-col`}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div className="flex items-center space-x-2">
            <Bot className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">AI学习助手</CardTitle>
            <Badge variant="secondary" className="text-xs">在线</Badge>
          </div>
          <div className="flex items-center space-x-1">
            <Button variant="ghost" size="sm" onClick={onMinimize}>
              {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
            </Button>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        {!isMinimized && (
          <CardContent className="flex-1 flex flex-col p-0">
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                      <div className={`flex items-start space-x-2 ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                          message.type === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                        }`}>
                          {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                        </div>
                        <div className={`rounded-lg p-3 ${
                          message.type === 'user' 
                            ? 'bg-primary text-primary-foreground' 
                            : 'bg-muted'
                        }`}>
                          <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                          
                          {message.codeExample && (
                            <div className="mt-3 p-3 bg-background rounded border">
                              <pre className="text-xs overflow-x-auto">
                                <code>{message.codeExample}</code>
                              </pre>
                            </div>
                          )}
                          
                          <div className="flex items-center justify-between mt-2">
                            <div className="text-xs opacity-70">
                              {message.timestamp.toLocaleTimeString()}
                            </div>
                            {message.type === 'ai' && (
                              <div className="flex items-center space-x-1">
                                <Button variant="ghost" size="sm" onClick={() => copyMessage(message.content)}>
                                  <Copy className="h-3 w-3" />
                                </Button>
                                <Button variant="ghost" size="sm" onClick={() => rateMessage(message.id, 'up')}>
                                  <ThumbsUp className="h-3 w-3" />
                                </Button>
                                <Button variant="ghost" size="sm" onClick={() => rateMessage(message.id, 'down')}>
                                  <ThumbsDown className="h-3 w-3" />
                                </Button>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      {message.suggestions && (
                        <div className="mt-2 flex flex-wrap gap-2">
                          {message.suggestions.map((suggestion, index) => (
                            <Button
                              key={index}
                              variant="outline"
                              size="sm"
                              className="text-xs"
                              onClick={() => handleSuggestionClick(suggestion)}
                            >
                              {suggestion}
                            </Button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {isTyping && (
                  <div className="flex justify-start">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                        <Bot className="h-4 w-4" />
                      </div>
                      <div className="bg-muted rounded-lg p-3">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
            
            {/* 快速操作按钮 */}
            <div className="p-4 border-t">
              <div className="flex flex-wrap gap-2 mb-3">
                <Button variant="outline" size="sm" onClick={() => handleSuggestionClick("解释当前知识点")}>
                  <Lightbulb className="h-3 w-3 mr-1" />
                  解释知识点
                </Button>
                <Button variant="outline" size="sm" onClick={() => handleSuggestionClick("给我一些练习题")}>
                  <BookOpen className="h-3 w-3 mr-1" />
                  练习题
                </Button>
                <Button variant="outline" size="sm" onClick={() => handleSuggestionClick("学习建议")}>
                  <HelpCircle className="h-3 w-3 mr-1" />
                  学习建议
                </Button>
              </div>
              
              {/* 输入区域 */}
              <div className="flex space-x-2">
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="输入你的问题..."
                    className="w-full px-3 py-2 border rounded-md text-sm pr-10"
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    className="absolute right-1 top-1/2 transform -translate-y-1/2"
                    onClick={handleVoiceInput}
                  >
                    {isListening ? <MicOff className="h-4 w-4 text-red-500" /> : <Mic className="h-4 w-4" />}
                  </Button>
                </div>
                <Button onClick={() => handleSendMessage()} disabled={!inputValue.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  )
}

export default AIChat

