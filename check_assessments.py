from backend.main import app
from backend.models.assessment import Assessment
from backend.extensions import db

with app.app_context():
    assessments = Assessment.query.all()
    print("\n=== 评估列表 ===")
    for assessment in assessments:
        print(f"\nID: {assessment.id}")
        print(f"标题: {assessment.title}")
        print(f"课程ID: {assessment.course_id}")
        print(f"是否发布: {assessment.is_published}")
        print(f"是否激活: {assessment.is_active}")
        print(f"创建时间: {assessment.created_at}")
        print("------------------------") 