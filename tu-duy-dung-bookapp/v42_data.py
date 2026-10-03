# -*- coding: utf-8 -*-
"""V4.2 learning/workbench assets. Designed to extend V2.7.x without altering source lessons."""

from datetime import date, timedelta

MULTI_CASES = [
    {
        "id":"mc_yield",
        "title_vi":"Yield giảm từ 99,2% xuống 96,8%",
        "title_en":"Yield drops from 99.2% to 96.8%",
        "intro_vi":"Line 2 giảm Yield trong hai ca liên tiếp. Chưa có bằng chứng rõ về nguyên nhân.",
        "intro_en":"Line 2 loses yield for two consecutive shifts. The cause is not yet verified.",
        "steps":[
            {
                "q_vi":"Bước đầu tiên nên làm gì?",
                "q_en":"What should you do first?",
                "options_vi":["Điều chỉnh parameter ngay","Breakdown dữ liệu theo machine/model/shift/lot","Yêu cầu supplier đổi vật liệu","Đào tạo lại operator"],
                "options_en":["Adjust parameters immediately","Break down data by machine/model/shift/lot","Ask the supplier to replace material","Retrain operators"],
                "answer":1,
                "why_vi":"Định vị pattern trước giúp tách Fact khỏi Assumption.",
                "why_en":"Locating the pattern first separates Facts from Assumptions."
            },
            {
                "q_vi":"Breakdown cho thấy lỗi tập trung ở Machine 3. Tiếp theo?",
                "q_en":"The breakdown shows the issue is concentrated on Machine 3. What next?",
                "options_vi":["Dừng toàn bộ line","So sánh parameter/condition Machine 3 với máy tốt","Kết luận Machine 3 hỏng","Bỏ qua vì chỉ một máy"],
                "options_en":["Stop the whole line","Compare Machine 3 parameters/conditions with a good machine","Conclude Machine 3 is broken","Ignore it because only one machine is affected"],
                "answer":1,
                "why_vi":"So sánh đối chứng giúp thu hẹp giả thuyết bằng evidence.",
                "why_en":"A controlled comparison narrows hypotheses with evidence."
            },
            {
                "q_vi":"Pressure của Machine 3 dao động bất thường. Bạn làm gì?",
                "q_en":"Machine 3 pressure is fluctuating abnormally. What do you do?",
                "options_vi":["Thay regulator có kiểm soát và theo dõi","Tăng spec để pass","Chỉ ghi nhận vào báo cáo","Đổi operator"],
                "options_en":["Replace the regulator in a controlled trial and monitor","Relax the spec to pass","Only record it in the report","Change the operator"],
                "answer":0,
                "why_vi":"Action phải gắn với cơ chế đã được xác nhận và có tiêu chí Check.",
                "why_en":"The action should target the verified mechanism and include Check criteria."
            },
            {
                "q_vi":"Sau khi defect giảm, bước cuối cùng là gì?",
                "q_en":"After the defect drops, what is the final step?",
                "options_vi":["Đóng dự án ngay","Chuẩn hóa setting/WI và theo dõi sustain","Xóa dữ liệu cũ","Chuyển sang vấn đề khác"],
                "options_en":["Close the project immediately","Standardize settings/WI and monitor sustainment","Delete old data","Move to another issue"],
                "answer":1,
                "why_vi":"PDCA chỉ hoàn tất khi kết quả được chuẩn hóa và duy trì.",
                "why_en":"PDCA is complete only when the result is standardized and sustained."
            }
        ]
    },
    {
        "id":"mc_delegation",
        "title_vi":"Kỹ sư mới lead một trial quan trọng",
        "title_en":"A new engineer leads an important trial",
        "intro_vi":"Manager muốn phát triển kỹ sư mới nhưng trial có rủi ro deadline.",
        "intro_en":"The manager wants to develop a new engineer, but the trial has deadline risk.",
        "steps":[
            {
                "q_vi":"Manager nên bắt đầu bằng gì?",
                "q_en":"What should the manager start with?",
                "options_vi":["Chỉ nói 'em xử lý giúp anh'","Chốt Outcome, Standard, Deadline và Authority","Tự làm phần khó","Gửi thật nhiều tài liệu"],
                "options_en":["Just say 'please handle it'","Agree Outcome, Standard, Deadline, and Authority","Do the difficult part personally","Send a large amount of material"],
                "answer":1,
                "why_vi":"Delegation cần rõ đầu ra và quyền hạn trước khi giao execution.",
                "why_en":"Delegation needs clear output and authority before execution begins."
            },
            {
                "q_vi":"Engineer gặp dữ liệu bất thường giữa trial. Cách tốt nhất?",
                "q_en":"The engineer sees abnormal data during the trial. Best response?",
                "options_vi":["Tự ý đổi toàn bộ plan","Dùng escalation rule/checkpoint đã thống nhất","Chờ đến cuối trial mới báo","Dừng project vô thời hạn"],
                "options_en":["Change the entire plan alone","Use the agreed escalation rule/checkpoint","Wait until the end to report it","Pause the project indefinitely"],
                "answer":1,
                "why_vi":"Checkpoint giúp giữ autonomy nhưng vẫn quản lý risk.",
                "why_en":"Checkpoints preserve autonomy while managing risk."
            },
            {
                "q_vi":"Sau trial, manager nên làm gì để phát triển năng lực?",
                "q_en":"After the trial, what should the manager do to build capability?",
                "options_vi":["Chỉ đánh giá đúng/sai","Review logic, feedback cụ thể và rút lesson","Lấy lại toàn bộ việc","Không cần review nếu pass"],
                "options_en":["Only judge pass/fail","Review the reasoning, give specific feedback, capture lessons","Take all the work back","Skip review if it passed"],
                "answer":1,
                "why_vi":"Learning loop biến delegation thành phát triển năng lực.",
                "why_en":"A learning loop turns delegation into capability development."
            }
        ]
    },
    {
        "id":"mc_supplier",
        "title_vi":"Chọn supplier khi giá bằng nhau",
        "title_en":"Choose a supplier when price is equal",
        "intro_vi":"Hai supplier có cùng giá nhưng khác quality history, delivery và risk.",
        "intro_en":"Two suppliers have equal price but different quality history, delivery, and risk.",
        "steps":[
            {
                "q_vi":"Bước đầu tiên?",
                "q_en":"First step?",
                "options_vi":["Chọn supplier quen","Chốt tiêu chí và trọng số trước khi chấm","Chọn delivery nhanh nhất","Bỏ qua risk"],
                "options_en":["Choose the familiar supplier","Agree criteria and weights before scoring","Choose the fastest delivery","Ignore risk"],
                "answer":1,
                "why_vi":"Trọng số phải được chốt trước khi biết kết quả để giảm bias.",
                "why_en":"Weights should be agreed before scoring to reduce bias."
            },
            {
                "q_vi":"Kết quả hai supplier sát nhau. Làm gì tiếp?",
                "q_en":"The two suppliers score very closely. What next?",
                "options_vi":["Chọn ngẫu nhiên","Sensitivity check và xem residual risk","Tăng trọng số cho supplier mình thích","Chỉ nhìn tổng điểm"],
                "options_en":["Choose randomly","Run sensitivity analysis and review residual risk","Increase the weight for your preferred supplier","Look only at total score"],
                "answer":1,
                "why_vi":"Sensitivity cho biết quyết định có ổn định khi giả định thay đổi hợp lý hay không.",
                "why_en":"Sensitivity shows whether the decision is robust to reasonable assumption changes."
            }
        ]
    }
]

WORKBENCH_TEMPLATES = [
    {
        "id":"5why","name_vi":"5 Why Worksheet","name_en":"5 Why Worksheet","category":"Problem Solving",
        "fields":[
            ("problem","Vấn đề / Problem"),
            ("why1","Why 1"),
            ("why2","Why 2"),
            ("why3","Why 3"),
            ("why4","Why 4"),
            ("why5","Why 5"),
            ("evidence","Bằng chứng chính / Key evidence"),
            ("root","Root Cause"),
            ("action","Action + Owner + Deadline")
        ]
    },
    {
        "id":"pdca","name_vi":"PDCA Planner","name_en":"PDCA Planner","category":"Improvement",
        "fields":[
            ("problem","Problem / Current condition"),
            ("target","Target"),
            ("plan","PLAN – Hypothesis & plan"),
            ("do","DO – Trial"),
            ("check","CHECK – Result vs baseline"),
            ("act","ACT – Standardize / Adjust"),
            ("owner","Owner"),
            ("deadline","Deadline")
        ]
    },
    {
        "id":"a3","name_vi":"A3 Thinking","name_en":"A3 Thinking","category":"Problem Solving",
        "fields":[
            ("background","Background"),
            ("current","Current condition"),
            ("target","Target condition"),
            ("analysis","Root cause analysis"),
            ("counter","Countermeasures"),
            ("follow","Follow-up / Sustain"),
            ("decision","Decision needed")
        ]
    },
    {
        "id":"raci","name_vi":"RACI Builder","name_en":"RACI Builder","category":"Management",
        "fields":[
            ("deliverable","Deliverable"),
            ("responsible","R – Responsible"),
            ("accountable","A – Accountable"),
            ("consulted","C – Consulted"),
            ("informed","I – Informed"),
            ("deadline","Deadline")
        ]
    },
    {
        "id":"risk","name_vi":"Risk Matrix","name_en":"Risk Matrix","category":"Risk",
        "fields":[
            ("risk","Risk description"),
            ("probability","Probability (1–5)"),
            ("impact","Impact (1–5)"),
            ("control","Existing / proposed control"),
            ("residual_p","Residual probability (1–5)"),
            ("residual_i","Residual impact (1–5)"),
            ("owner","Risk owner")
        ]
    },
    {
        "id":"decision","name_vi":"Decision Matrix","name_en":"Decision Matrix","category":"Decision",
        "fields":[
            ("decision","Decision question"),
            ("options","Options (comma separated)"),
            ("criteria","Criteria (comma separated)"),
            ("weights","Weights (comma separated, e.g. 40,30,30)"),
            ("notes","Scores / evidence notes"),
            ("risk","Residual risk / sensitivity notes")
        ]
    },
    {
        "id":"skill","name_vi":"Skill Matrix Plan","name_en":"Skill Matrix Plan","category":"People",
        "fields":[
            ("skill","Critical skill"),
            ("current","Current coverage / levels"),
            ("target","Target coverage"),
            ("gap","Gap"),
            ("training","Training / coaching action"),
            ("backup","Backup person"),
            ("date","Target date")
        ]
    }
]

def default_review_state(lesson_ids):
    today=date.today().isoformat()
    return {lid:{"level":0,"due":today,"reviews":0} for lid in lesson_ids}

def next_review(level):
    days=[0,1,3,7,14,30,60]
    nxt=min(level+1,len(days)-1)
    return nxt,(date.today()+timedelta(days=days[nxt])).isoformat()

def flashcard_for_lesson(vi,en):
    blocks=vi.get("blocks") or []
    eblocks=en.get("blocks") or []
    front_vi=vi["title"]
    front_en=en["title"]
    if blocks and eblocks:
        back_vi=" • ".join(f"{b[0]}: {b[1]}" for b in blocks)
        back_en=" • ".join(f"{b[0]}: {b[1]}" for b in eblocks)
    else:
        back_vi=vi.get("summary","")
        back_en=en.get("summary","")
    return {"front_vi":front_vi,"front_en":front_en,"back_vi":back_vi,"back_en":back_en}
