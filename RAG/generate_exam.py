import os
import sys
import json
import yaml
import argparse
import traceback
import re
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Constants
PROMPT_FILE = Path(__file__).parent / "prompts" / "zh.yaml"

class ExamGenerator:
    def __init__(self, course_id: str, output_dir="assignments"):
        self.course_id = course_id
        self.client = self._init_openai_client()
        self.prompts = self._load_prompts()
        self.course_name = self._get_course_name()
        self.output_dir = Path(output_dir)
        
        # 创建输出目录(如果不存在)
        self.output_dir.mkdir(exist_ok=True)
        
        self.exam_data = {
            "title": f"{self.course_name}期末考试",
            "course": self.course_name,
            "duration": "120分钟",
            "total_score": 100,
            "sections": []
        }

    def _init_openai_client(self) -> OpenAI:
        """初始化OpenAI客户端"""
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_API_BASE")
        
        if not api_key or not base_url:
            raise ValueError("在.env文件中未找到LLM_API_KEY或LLM_API_BASE")
        
        return OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def _load_prompts(self) -> Dict:
        """从YAML文件加载提示词"""
        if not PROMPT_FILE.exists():
            raise FileNotFoundError(f"未找到提示词文件: {PROMPT_FILE}")
        
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _get_course_name(self) -> str:
        """从元数据文件获取课程名称"""
        metadata_path = Path(f"./data/{self.course_id}/metadata.json")
        if metadata_path.exists():
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    return metadata.get("course_name", f"课程 {self.course_id}")
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return f"课程 {self.course_id}"

    def _get_context_from_rag(self, query: str) -> str:
        """通过查询RAG系统获取上下文"""
        try:
            # Import here to avoid circular imports
            from rag_query import hybrid_retriever, format_docs
            
            # Call the hybrid retriever to get relevant documents
            docs = hybrid_retriever(query, self.course_id)
            
            # Format documents into a single string context
            context = format_docs(docs)
            
            # Truncate if too long (optional)
            max_context_length = 8000  # Adjust as needed
            if len(context) > max_context_length:
                print(f"警告：上下文太长({len(context)}字符)，截断至{max_context_length}字符...")
                context = context[:max_context_length] + "..."
            
            # 确保上下文非空
            if not context.strip():
                print("警告：获取到的上下文为空，使用通用提示代替")
                return f"提供关于{self.course_name}的教学资料，包含课程的关键概念和知识点。"
                
            return context
        except Exception as e:
            print(f"获取RAG上下文时出错: {str(e)}")
            print("使用通用上下文继续...")
            return f"提供关于{self.course_name}的教学资料，包含课程的关键概念和知识点。"
            
    def _extract_questions_from_text(self, text, question_type="multiple_choice"):
        """尝试从文本中提取问题，即使JSON解析失败"""
        questions = []
        
        # 先尝试解析JSON
        try:
            # 移除可能的markdown代码块标记
            text = re.sub(r'```(?:json)?|```', '', text)
            
            # 尝试解析JSON
            data = json.loads(text)
            if isinstance(data, dict) and "questions" in data and isinstance(data["questions"], list):
                questions = data["questions"]
                print(f"成功从JSON中提取了 {len(questions)} 道题目")
                return questions
        except Exception:
            print("无法使用JSON解析，尝试通过文本提取...")
        
        # 如果无法解析JSON，尝试通过文本模式提取问题
        try:
            if question_type == "multiple_choice":
                # 正则表达式匹配选择题模式
                pattern = r'"id":\s*(\d+),\s*"stem":\s*"([^"]+)",\s*"options":\s*\[\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)"\s*\],\s*"answer":\s*"([^"]+)",\s*"explanation":\s*"([^"]+)"'
                matches = re.finditer(pattern, text)
                
                for match in matches:
                    try:
                        id_num, stem, option_a, option_b, option_c, option_d, answer, explanation = match.groups()
                        question = {
                            "id": int(id_num),
                            "stem": stem,
                            "options": [option_a, option_b, option_c, option_d],
                            "answer": answer,
                            "explanation": explanation
                        }
                        questions.append(question)
                    except Exception as e:
                        print(f"解析选择题时出错: {str(e)}")
                
            elif question_type == "fill_in_blank":
                # 正则表达式匹配填空题模式
                pattern = r'"id":\s*(\d+),\s*"stem":\s*"([^"]+)",\s*"answer":\s*"([^"]+)",\s*"explanation":\s*"([^"]+)"'
                matches = re.finditer(pattern, text)
                
                for match in matches:
                    try:
                        id_num, stem, answer, explanation = match.groups()
                        question = {
                            "id": int(id_num),
                            "stem": stem,
                            "answer": answer,
                            "explanation": explanation
                        }
                        questions.append(question)
                    except Exception as e:
                        print(f"解析填空题时出错: {str(e)}")
                
            elif question_type == "essay":
                # 正则表达式匹配论述题模式
                pattern = r'"id":\s*(\d+),\s*"stem":\s*"([^"]+)",\s*"reference_answer":\s*"([^"]+)",\s*"grading_criteria":\s*"([^"]+)"'
                matches = re.finditer(pattern, text)
                
                for match in matches:
                    try:
                        id_num, stem, reference_answer, grading_criteria = match.groups()
                        question = {
                            "id": int(id_num),
                            "stem": stem,
                            "reference_answer": reference_answer,
                            "grading_criteria": grading_criteria
                        }
                        questions.append(question)
                    except Exception as e:
                        print(f"解析论述题时出错: {str(e)}")
            
            print(f"通过文本模式提取出 {len(questions)} 道题目")
            
        except Exception as e:
            print(f"文本提取方式出错: {str(e)}")
        
        return questions

    def _call_llm(self, prompt: str, question_type="multiple_choice") -> Dict:
        """调用LLM并返回解析后的JSON响应"""
        model_name = os.getenv("LLM_MODEL", "")
        if not model_name:
            raise ValueError("在.env文件中未找到LLM_MODEL")
        
        try:
            print("正在调用LLM生成内容...")
            
            # 添加明确的JSON格式要求
            prompt_with_json_format = prompt + "\n\n请确保返回格式正确的JSON，必须包含questions数组，即使没有任何题目也应返回空数组。请不要在JSON外包含其他内容，不要添加额外的字段。"
            
            # 设置更高温度以增加创造性，但不要太高
            temperature = 0.75
            
            # 允许更长的输出和更长的思考时间
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt_with_json_format}],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=2000,
                timeout=120,  # 允许更长的响应时间
                seed=42,  # 使用固定的随机种子以提高一致性
            )
            
            json_text = response.choices[0].message.content
            
            # 检查是否为空内容
            if not json_text.strip():
                print("警告: LLM返回空内容")
                return {"questions": []}
                
            # 尝试提取问题（优先尝试JSON解析，失败则使用文本提取）
            questions = self._extract_questions_from_text(json_text, question_type)
            
            # 确保每个问题都有唯一ID
            for i, q in enumerate(questions):
                if "id" not in q:
                    q["id"] = i + 1
            
            return {"questions": questions}
                
        except Exception as e:
            print(f"调用LLM时发生错误: {str(e)}")
            traceback.print_exc()
            # 返回默认空结构
            return {"questions": []}

    def generate_multiple_choice(self, num_questions=5) -> Dict:
        """生成选择题"""
        print(f"\n🔍 正在为选择题收集上下文...")
        context = self._get_context_from_rag(f"{self.course_name}的关键概念和知识点是什么？")
        
        print(f"📝 正在生成{num_questions}道选择题...")
        prompt_template = self.prompts["multiple_choice"]
        prompt = prompt_template.replace("{num_questions}", str(num_questions)).replace("{context}", context)
        
        # 如果上下文内容较少，增加更多引导
        if len(context) < 200:
            prompt += f"\n\n即使上下文信息有限，也请尽力生成{num_questions}道高质量的选择题。可以使用你的知识适当扩展相关内容。"
            
        # 使用指令微调，增加精确性
        prompt += "\n\n请注意:\n1. 每个问题必须有四个选项(A、B、C、D)\n2. 每个问题必须有明确的答案(答案为选项的字母，如'A')\n3. 每个问题必须有解释\n4. 以标准JSON格式返回，不要添加额外字段\n5. 假设我是TensorFlow Lite和移动端AI应用方面的专家，请生成适合我的题目"
            
        # 尝试多次调用以获取有效结果
        max_attempts = 3
        result = {"questions": []}
        
        for attempt in range(max_attempts):
            if attempt > 0:
                print(f"第{attempt+1}次尝试生成选择题...")
            
            attempt_result = self._call_llm(prompt, "multiple_choice")
            if attempt_result.get("questions") and len(attempt_result["questions"]) > 0:
                result = attempt_result
                break
            
            if attempt < max_attempts - 1:
                print(f"未能生成选择题，将进行重试...")
        
        section = {
            "type": "multiple_choice",
            "description": "选择题：请在每小题给出的选项中选出一个正确答案。",
            "score_per_question": 4,  # 每道题4分
            "questions": result.get("questions", [])
        }
        
        self.exam_data["sections"].append(section)
        print(f"✅ 已生成{len(section['questions'])}道选择题。")
        
        # 立即保存当前阶段结果
        self._save_section_results("multiple_choice")
        
        return result

    def generate_fill_in_blank(self, num_questions=5) -> Dict:
        """生成填空题"""
        print(f"\n🔍 正在为填空题收集上下文...")
        context = self._get_context_from_rag(f"{self.course_name}中重要的术语、定义和公式是什么？")
        
        print(f"📝 正在生成{num_questions}道填空题...")
        prompt_template = self.prompts["fill_in_blank"]
        prompt = prompt_template.replace("{num_questions}", str(num_questions)).replace("{context}", context)
        
        # 如果上下文内容较少，增加更多引导
        if len(context) < 200:
            prompt += f"\n\n即使上下文信息有限，也请尽力生成{num_questions}道高质量的填空题。可以使用你的知识适当扩展相关内容。"
            
        # 使用指令微调，增加精确性
        prompt += "\n\n请注意:\n1. 每个填空题只有一个空，用'_____'表示\n2. 每个问题必须有明确的答案\n3. 每个问题必须有解释\n4. 以标准JSON格式返回，不要添加额外字段\n5. 题目应该围绕TensorFlow Lite和移动端AI应用的核心概念"
            
        # 尝试多次调用以获取有效结果
        max_attempts = 3
        result = {"questions": []}
        
        for attempt in range(max_attempts):
            if attempt > 0:
                print(f"第{attempt+1}次尝试生成填空题...")
            
            attempt_result = self._call_llm(prompt, "fill_in_blank")
            if attempt_result.get("questions") and len(attempt_result["questions"]) > 0:
                result = attempt_result
                break
            
            if attempt < max_attempts - 1:
                print(f"未能生成填空题，将进行重试...")
        
        section = {
            "type": "fill_in_blank",
            "description": "填空题：请在横线上填写正确的内容。",
            "score_per_question": 4,  # 每道题4分
            "questions": result.get("questions", [])
        }
        
        self.exam_data["sections"].append(section)
        print(f"✅ 已生成{len(section['questions'])}道填空题。")
        
        # 立即保存当前阶段结果
        self._save_section_results("fill_in_blank")
        
        return result

    def generate_essay_questions(self, num_questions=3) -> Dict:
        """生成论述题"""
        print(f"\n🔍 正在为论述题收集上下文...")
        context = self._get_context_from_rag(f"{self.course_name}中需要深入理解的复杂主题是什么？")
        
        print(f"📝 正在生成{num_questions}道论述题...")
        prompt_template = self.prompts["essay_questions"]
        prompt = prompt_template.replace("{num_questions}", str(num_questions)).replace("{context}", context)
        
        # 如果上下文内容较少，增加更多引导
        if len(context) < 200:
            prompt += f"\n\n即使上下文信息有限，也请尽力生成{num_questions}道高质量的论述题。可以使用你的知识适当扩展相关内容。"
            
        # 使用指令微调，增加精确性
        prompt += "\n\n请注意:\n1. 每个题目必须有stem（题干）\n2. 每个题目必须有reference_answer（参考答案）\n3. 每个题目必须有grading_criteria（评分标准）\n4. 以标准JSON格式返回，不要添加额外字段\n5. 围绕TensorFlow Lite和移动端深度学习应用的实践问题设置论述题"
            
        # 尝试多次调用以获取有效结果
        max_attempts = 3
        result = {"questions": []}
        
        for attempt in range(max_attempts):
            if attempt > 0:
                print(f"第{attempt+1}次尝试生成论述题...")
            
            attempt_result = self._call_llm(prompt, "essay")
            if attempt_result.get("questions") and len(attempt_result["questions"]) > 0:
                result = attempt_result
                break
            
            if attempt < max_attempts - 1:
                print(f"未能生成论述题，将进行重试...")
        
        section = {
            "type": "essay",
            "description": "论述题：请按要求回答以下问题。",
            "score_per_question": 20,  # 每道题20分
            "questions": result.get("questions", [])
        }
        
        self.exam_data["sections"].append(section)
        print(f"✅ 已生成{len(section['questions'])}道论述题。")
        
        # 立即保存当前阶段结果
        self._save_section_results("essay")
        
        return result
        
    def _save_section_results(self, section_type: str) -> None:
        """保存当前生成的部分"""
        # 找到当前节
        current_section = None
        for section in self.exam_data["sections"]:
            if section["type"] == section_type:
                current_section = section
                break
        
        if current_section is None:
            print(f"警告: 未找到类型为 {section_type} 的部分")
            return
            
        # 创建单独的文件名
        section_file = self.output_dir / f"{self.course_id}_{section_type}.json"
        
        # 保存该部分
        with open(section_file, "w", encoding="utf-8") as f:
            json.dump(current_section, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已保存{section_type}部分至 {section_file}")
        
        # 打印生成的题目预览
        questions = current_section.get("questions", [])
        if questions:
            print("\n--- 生成的题目预览 ---")
            for q in questions[:2]:  # 只预览前两题
                print(f"题目 {q['id']}: {q['stem'][:50]}..." if len(q['stem']) > 50 else f"题目 {q['id']}: {q['stem']}")
                if "options" in q:
                    print(f"  选项: {', '.join(o[:20] + '...' if len(o) > 20 else o for o in q['options'][:2])}")
                    print(f"  答案: {q['answer']}")
                elif "answer" in q:
                    print(f"  答案: {q['answer']}")
        else:
            print("未生成任何题目！")

    def save_exam(self, output_path=None) -> str:
        """保存生成的考试到JSON文件"""
        if output_path is None:
            output_path = self.output_dir / f"exam_{self.course_id}.json"
        else:
            # 确保输出路径是Path对象
            output_path = Path(output_path)
            # 如果只提供了文件名，则放在输出目录下
            if not output_path.is_absolute() and len(output_path.parts) == 1:
                output_path = self.output_dir / output_path
        
        # 计算实际总分
        total_score = 0
        for section in self.exam_data["sections"]:
            total_score += section["score_per_question"] * len(section["questions"])
        self.exam_data["total_score"] = total_score
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.exam_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 考试已保存至 {output_path}")
        return str(output_path)
    
    def print_section_summary(self, section_type: str) -> None:
        """打印生成的部分摘要"""
        for section in self.exam_data["sections"]:
            if section["type"] == section_type:
                questions = section["questions"]
                print(f"\n--- {section['description']} ---")
                for q in questions:
                    print(f"题目 {q['id']}: {q['stem'][:50]}..." if len(q['stem']) > 50 else f"题目 {q['id']}: {q['stem']}")

def generate_final_exam(course_id, output_path=None, output_dir="assignments"):
    """为指定课程生成完整考试"""
    generator = ExamGenerator(course_id, output_dir=output_dir)
    
    try:
        # 步骤1: 生成选择题
        generator.generate_multiple_choice(num_questions=10)
        generator.print_section_summary("multiple_choice")
        
        # 步骤2: 生成填空题
        generator.generate_fill_in_blank(num_questions=5)
        generator.print_section_summary("fill_in_blank")
        
        # 步骤3: 生成论述题
        generator.generate_essay_questions(num_questions=3)
        generator.print_section_summary("essay")
        
        # 保存完整考试
        output_file = generator.save_exam(output_path)
        
        print(f"\n✨ 考试生成完成! ✨")
        print(f"总题目数: {sum(len(section['questions']) for section in generator.exam_data['sections'])}")
        print(f"总分: {generator.exam_data['total_score']}")
        
        return output_file
    except Exception as e:
        print(f"生成考试时发生错误: {str(e)}")
        traceback.print_exc()
        # 尽量保存已经生成的内容
        try:
            if generator.exam_data["sections"]:
                output_file = generator.save_exam(output_path)
                print(f"已保存部分生成的考试内容到 {output_file}")
        except:
            print("保存部分结果失败")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="为课程生成期末考试。")
    parser.add_argument("--course_id", type=str, required=True, help="要生成考试的课程ID。")
    parser.add_argument("--output", type=str, help="保存生成的考试JSON文件的路径。")
    parser.add_argument("--output_dir", type=str, default="assignments", help="保存生成的考试文件的目录。")
    args = parser.parse_args()
    
    generate_final_exam(args.course_id, args.output, args.output_dir) 