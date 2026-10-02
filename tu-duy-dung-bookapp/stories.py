# -*- coding: utf-8 -*-
"""Memorable mini-stories for all 40 lessons in Book App V2.6.
Stories are fictional but grounded in realistic workplace situations.
"""

STORIES = {
"1.1":{
"title":"Ca đêm và chiếc máy bị oan",
"story":"22:10, line đóng gói báo NG tăng gấp ba. Minh, kỹ sư trẻ, nhìn thấy máy số 2 vừa được bảo trì và nói ngay: “Chắc chắn do máy”. Trưởng ca Lan không cho dừng máy. Cô yêu cầu Minh viết ra ba cột: điều biết chắc, điều đang đoán và điều cần kiểm tra. Dữ kiện cho thấy lỗi xuất hiện ở cả máy 1 và máy 2, nhưng chỉ trên một lot vật liệu mới. Sau 20 phút, team phát hiện độ dày liner của lot này lệch so với lịch sử. Nếu nghe theo phán đoán đầu tiên, họ đã mất thêm một giờ tháo máy mà vẫn không giải quyết được gì.",
"memory":"Tư duy tốt bắt đầu bằng việc tách sự thật khỏi suy đoán trước khi hành động."
},
"1.2":{
"title":"Ba câu nói trong cùng một cuộc họp",
"story":"Trong cuộc họp sáng, ba người nói về cùng một vấn đề. QA nói: “NG hôm qua là 2,8%.” PE nói: “Máy này chạy không ổn định.” Purchasing nói: “Có lẽ do supplier mới.” Trưởng phòng viết ba câu lên bảng rồi đánh dấu F – O – A. Câu đầu là Fact vì có dữ liệu; câu thứ hai là Opinion vì chưa có định nghĩa ‘không ổn định’; câu thứ ba là Assumption vì chưa có kiểm chứng. Chỉ một thao tác nhỏ này đã khiến cuộc họp đổi từ tranh luận cảm tính sang danh sách việc cần xác minh.",
"memory":"Khi biết câu nào là Fact, Opinion hay Assumption, cuộc họp sẽ bớt tranh cãi và tăng kiểm chứng."
},
"1.3":{
"title":"Báo cáo cải tiến quá đẹp",
"story":"Một nhóm báo cáo defect giảm từ 1,1% xuống 0,3% sau action mới. Slide rất đẹp và mọi người chuẩn bị chốt dự án. Hùng hỏi đúng một câu: “Cỡ mẫu và model mix trước–sau có giống nhau không?” Khi mở dữ liệu gốc, team phát hiện tuần sau action chỉ chạy model dễ, trong khi baseline có cả model khó. Kết luận ‘đã fix’ bị rút lại. Nhóm tiếp tục theo dõi thêm hai tuần và mới xác nhận gain thật là 0,4%.",
"memory":"Tư duy phản biện không phá hỏng thành tích; nó bảo vệ team khỏi kết luận sai."
},
"1.4":{
"title":"Hai người cho một công việc một người",
"story":"Tại một công đoạn kiểm tra, hai operator luôn đứng cạnh nhau vì “từ lúc mở line đã làm vậy”. Quản lý mới hỏi: “Nếu hôm nay thiết kế công đoạn từ đầu, điều gì bắt buộc phải có hai người?” Sau khi quay video thao tác, team thấy chỉ có 18 giây khi xoay jig cần người thứ hai. Họ thiết kế thêm một chốt giữ đơn giản, phần còn lại chỉ cần một operator. Năng suất tăng mà không tăng tốc thao tác.",
"memory":"First Principles giúp nhìn lại điều từng được xem là ‘đương nhiên’."
},
"2.1":{
"title":"Từ Yield thấp đến một regulator nhỏ",
"story":"Yield giảm 2%. Ban đầu mọi người đưa ra 11 giả thuyết. Kỹ sư Trang ép team đi theo một chuỗi logic: hiện tượng ở đâu, dữ liệu cho thấy gì, giả thuyết nào phù hợp, test nào phân biệt được. Breakdown chỉ ra lỗi tập trung ở máy 3; test pressure cho thấy regulator dao động; thay regulator thì defect biến mất. Một vấn đề tưởng phức tạp được thu về một chuỗi logic có thể kiểm tra.",
"memory":"Logic tốt biến ‘rất nhiều khả năng’ thành một đường đi có bằng chứng."
},
"2.2":{
"title":"Operator sai hay hệ thống cho phép sai?",
"story":"Một operator nhập nhầm 180 thay vì 108. Manager định ra thông báo nhắc nhở toàn line. PE hỏi: “Nếu operator khác làm cùng thao tác, hệ thống có ngăn được không?” Câu trả lời là không. HMI cho phép nhập mọi giá trị và WI chỉ ghi bằng chữ nhỏ. Team thêm giới hạn nhập, màu cảnh báo và recipe lock. Từ đó lỗi không tái diễn dù có nhiều operator mới.",
"memory":"Đừng chỉ sửa người; hãy sửa điều kiện khiến lỗi có thể xảy ra."
},
"2.3":{
"title":"Bảng Pareto không ai hiểu",
"story":"Báo cáo defect có các nhóm: Machine 1, Night shift, Scratch, Model X và Others. Manager nhìn 30 giây rồi hỏi: “Các nhóm này có cùng một tiêu chí không?” Cả team im lặng. Sau đó họ tách thành ba breakdown riêng: theo machine, theo shift và theo defect type. Chỉ khi đó mới thấy Scratch chiếm 54% và chủ yếu xuất hiện ở Machine 1 ca đêm.",
"memory":"MECE không phải thuật ngữ đẹp; nó làm dữ liệu trở nên có thể suy luận."
},
"2.4":{
"title":"Một lỗi, ba nguyên nhân cùng lúc",
"story":"Scrap tăng nhưng không có một root cause đơn lẻ. Map nguyên nhân cho thấy material thickness tăng nhẹ, machine pressure ở biên thấp và camera detect yếu hơn ở model màu tối. Từng yếu tố riêng lẻ vẫn trong giới hạn, nhưng khi ba điều kiện cùng xuất hiện thì lỗi bùng lên. Team điều chỉnh cả material window, setting và detection rule.",
"memory":"Một hệ quả đôi khi là sản phẩm của nhiều yếu tố tương tác, không phải một nguyên nhân duy nhất."
},
"3.1":{
"title":"Why thứ năm mới chạm hệ thống",
"story":"Máy dừng vì sensor lệch. Why 1: sensor lệch. Why 2: bracket lỏng. Why 3: screw bị xoay sau bảo trì. Why 4: torque không được kiểm soát. Why 5: WI bảo trì không quy định torque và không có check sau lắp. Nếu dừng ở ‘bracket lỏng’, team chỉ siết lại screw; đi sâu hơn giúp họ sửa chuẩn bảo trì để lỗi không quay lại.",
"memory":"5 Why tốt không tìm người để đổ lỗi; nó tìm cơ chế để ngăn tái diễn."
},
"3.2":{
"title":"Con cá xương cứu một cuộc tranh luận",
"story":"Defect trắng viền xuất hiện sau die-cut. Production nói do material, Supplier nói do machine, QA nói do handling. Thay vì tranh luận, PE vẽ Fishbone và cho từng nhóm ghi giả thuyết vào Man–Machine–Material–Method–Measurement–Environment. Sau đó mỗi nhánh phải có test. Ba ngày sau, họ loại được 80% giả thuyết và xác nhận dao cắt cùng tension là hai driver chính.",
"memory":"Fishbone mở rộng góc nhìn; evidence mới quyết định nhánh nào đúng."
},
"3.3":{
"title":"100 lỗi nhưng chỉ hai lỗi đáng tập trung",
"story":"Một tuần có 100 defect thuộc 17 loại. Team chia người xử lý tất cả và không lỗi nào giảm đáng kể. Khi vẽ Pareto, hai defect đầu chiếm 71%. Họ dồn nguồn lực vào hai nhóm này, sau một tuần total NG giảm gần một nửa. Các lỗi còn lại vẫn tồn tại, nhưng giờ team có thời gian xử lý theo thứ tự.",
"memory":"Ưu tiên không có nghĩa bỏ qua; ưu tiên là chọn nơi tạo impact lớn nhất trước."
},
"3.4":{
"title":"Action tốt nhưng chưa phải cải tiến",
"story":"PE thay parameter và defect giảm mạnh trong 2 ngày. Mọi người ăn mừng rồi chuyển sang dự án khác. Một tuần sau ca đêm dùng recipe cũ và lỗi quay lại. Team nhận ra họ đã làm Plan–Do–Check nhưng chưa Act. Sau đó recipe được lock, WI cập nhật và operator được training. Từ đó kết quả mới được duy trì.",
"memory":"Gain chưa được chuẩn hóa vẫn chỉ là một thử nghiệm thành công."
},
"4.1":{
"title":"Quyết định supplier không thể chỉ nhìn giá",
"story":"Hai supplier cùng báo giá 1,00 USD. Purchasing muốn chọn bên giao nhanh hơn. QA đưa dữ liệu variation; PMC đưa delivery history; PE đưa kết quả trial. Khi đặt tất cả lên cùng bàn, supplier có lead time nhanh lại gây risk line stop cao hơn. Team chấp nhận lead time dài thêm một ngày để đổi lấy stability.",
"memory":"Dữ liệu đúng giúp nhìn thấy chi phí và rủi ro mà giá đơn vị không thể hiện."
},
"4.2":{
"title":"Giảm 50% nhưng thật ra không biết giảm từ đâu",
"story":"Một dự án ghi mục tiêu ‘giảm defect 50%’. Khi review, manager hỏi baseline là tuần nào. Không ai thống nhất: người dùng 1 tuần, người dùng 1 tháng, model mix khác nhau. Team quay lại chốt baseline 4 tuần cùng product mix và target cụ thể. Từ đó mọi người mới nói cùng một ngôn ngữ khi đánh giá gain.",
"memory":"Không có baseline đáng tin, phần trăm cải tiến chỉ là một con số đẹp."
},
"4.3":{
"title":"Cuộc tranh luận giữa Giá và Chất lượng",
"story":"Purchasing chọn A vì rẻ hơn 3%; QA chọn B vì Cpk tốt hơn; PMC thích C vì giao nhanh. Cuộc họp kéo dài mà không ai thuyết phục được ai. Manager yêu cầu lập Decision Matrix với 5 tiêu chí và trọng số thống nhất trước khi chấm. Kết quả không làm mọi người cùng sở thích, nhưng làm lý do quyết định trở nên minh bạch.",
"memory":"Decision Matrix không quyết định thay con người; nó làm trade-off hiện rõ."
},
"4.4":{
"title":"Một gain nhỏ và một rủi ro rất lớn",
"story":"Thay đổi setting có thể tăng yield 0,2%, nhưng làm detection margin của một lỗi customer-critical nhỏ đi đáng kể. Nếu chỉ nhìn gain, action có vẻ hấp dẫn. Khi đánh probability × impact, risk khách hàng vượt ngưỡng chấp nhận. Team chọn một giải pháp gain thấp hơn nhưng an toàn hơn.",
"memory":"Một lợi ích nhỏ không nên che khuất một hậu quả lớn."
},
"5.1":{
"title":"Ngày nào cũng bận nhưng việc quan trọng vẫn trễ",
"story":"Mai trả lời email, họp đột xuất và xử lý yêu cầu nhỏ cả ngày. Cuối tuần, dự án cải tiến quan trọng vẫn chưa bắt đầu. Khi đưa task vào Eisenhower Matrix, cô nhận ra mình dành phần lớn thời gian cho việc khẩn nhưng ít quan trọng. Tuần sau, cô khóa hai buổi sáng cho dự án trước khi mở email.",
"memory":"Việc quan trọng thường không hét lên; nếu không bảo vệ thời gian, nó sẽ luôn bị việc khẩn lấn át."
},
"5.2":{
"title":"90 phút không notification",
"story":"Nam cần phân tích DOE nhưng cứ 5 phút lại trả lời chat. Sau ba giờ, anh vẫn chưa xong. Ngày hôm sau, anh chặn 9:00–10:30, tắt notification và báo team chỉ gọi nếu line stop. 90 phút đó tạo ra nhiều tiến triển hơn cả buổi hôm trước.",
"memory":"Time Blocking không tạo thêm giờ; nó bảo vệ chất lượng của giờ đang có."
},
"5.3":{
"title":"14 việc đều ở trạng thái 90%",
"story":"Một engineer có 14 action ‘gần xong’. Mỗi ngày anh chuyển qua lại giữa các task và deadline liên tục trễ. Manager đặt WIP limit = 3. Việc mới phải chờ backlog trừ khi một việc đang làm được đóng. Sau hai tuần, số task hoàn thành tăng dù số task ‘đang làm’ giảm mạnh.",
"memory":"Bắt đầu ít hơn có thể giúp hoàn thành nhiều hơn."
},
"5.4":{
"title":"30 phút thứ Sáu cứu cả tuần sau",
"story":"Hằng tuần, team luôn phát hiện deadline trễ quá muộn. Leader bắt đầu một Weekly Review 30 phút: xem calendar, waiting list, project và Top 3 tuần tới. Ngay tuần đầu, họ phát hiện một sample phải gửi trước thứ Ba nhưng chưa ai đặt logistics. Một việc nhỏ được xử lý trước khi trở thành khủng hoảng.",
"memory":"Review đều đặn biến bất ngờ thành việc có thể chuẩn bị."
},
"6.1":{
"title":"Giao việc một câu và ba ngày làm lại",
"story":"Manager nói với kỹ sư mới: “Em lead trial này giúp anh.” Ba ngày sau, engineer mang kết quả nhưng thiếu acceptance criteria, sample size và format report. Manager thất vọng, engineer cũng thất vọng. Lần sau họ thống nhất Outcome, Authority, Deadline và Checkpoint ngay từ đầu. Trial thứ hai chạy trơn tru và engineer tự tin hơn hẳn.",
"memory":"Delegation tốt không chỉ giao việc; nó giao sự rõ ràng."
},
"6.2":{
"title":"Manager ngừng trả lời trong 10 phút",
"story":"Mỗi khi kỹ sư hỏi, trưởng nhóm thường đưa ngay đáp án. Một ngày anh thử chỉ hỏi: “Mục tiêu là gì? Em thấy dữ liệu nói gì? Có ba lựa chọn nào?” Ban đầu cuộc nói chuyện chậm hơn, nhưng sau vài tuần engineer bắt đầu tự mang phương án thay vì mang câu hỏi.",
"memory":"Coaching hy sinh chút tốc độ hôm nay để tăng năng lực ngày mai."
},
"6.3":{
"title":"‘Em cẩu thả’ và một cách nói khác",
"story":"Một manager định nói: “Em quá cẩu thả.” HR gợi ý anh đổi sang SBI: “Trong báo cáo sáng nay, phần baseline bị thiếu nên team không thể chốt quyết định. Lần sau hãy kiểm tra checklist trước khi gửi.” Cùng một vấn đề, nhưng người nhận không cảm thấy bị gắn nhãn và biết chính xác cần sửa gì.",
"memory":"Feedback tốt nói về hành vi và tác động, không phán xét con người."
},
"6.4":{
"title":"Ngày senior nghỉ phép",
"story":"Một process quan trọng chỉ có Tuấn biết setup. Khi Tuấn nghỉ, line mất 4 giờ chờ hỗ trợ từ xa. Sau sự cố, team làm Skill Matrix và phát hiện thêm ba kỹ năng khác cũng chỉ có một người level cao. Họ lập kế hoạch backup trong 3 tháng. Lần nghỉ phép tiếp theo, line vẫn chạy bình thường.",
"memory":"Skill Matrix biến rủi ro ‘mọi người đều biết’ thành gap có thể hành động."
},
"7.1":{
"title":"‘Cải thiện defect’ không phải mục tiêu",
"story":"KPI quý ghi ‘Cải thiện defect A’. Cuối quý, team tranh luận đã hoàn thành hay chưa vì defect có giảm nhưng không ai biết mức nào là đủ. Quý sau họ viết: giảm từ 1,2% xuống ≤0,6% trước 30/11 trên Line 2. Từ đó mọi action đều hướng vào một đích rõ ràng.",
"memory":"Mục tiêu rõ giúp kết thúc tranh luận về việc đã Done hay chưa."
},
"7.2":{
"title":"20 cuộc họp nhưng KPI vẫn xấu",
"story":"Một team tự hào vì đã tổ chức 20 cuộc review. Manager hỏi: “KPI nào tốt lên vì 20 cuộc họp đó?” Không ai trả lời. Họ phân biệt Activity và Outcome: họp chỉ là activity; OEE, defect và lead time mới là outcome. Một số cuộc họp bị bỏ, nhưng action chất lượng hơn.",
"memory":"Bận rộn không đồng nghĩa tạo kết quả."
},
"7.3":{
"title":"Đợi customer claim mới biết có vấn đề",
"story":"Team chỉ theo dõi customer claim. Khi chỉ số xấu, sản phẩm đã ra khỏi nhà máy nhiều ngày. Họ thêm leading indicators: Cpk critical dimension, audit compliance và alarm rate. Một tháng sau, Cpk bắt đầu giảm dù chưa có claim; team can thiệp sớm và tránh được lô lỗi lớn.",
"memory":"Leading indicator cho cơ hội hành động trước khi lagging result xuất hiện."
},
"7.4":{
"title":"Daily review cho mọi thứ",
"story":"Một phòng review 25 KPI mỗi sáng. Meeting kéo dài 90 phút và đa số chỉ số gần như không đổi theo ngày. Họ phân lại: operation daily, action weekly, cost saving monthly. Meeting sáng còn 25 phút và thảo luận sâu hơn vào những chỉ số thật sự cần phản ứng nhanh.",
"memory":"Cadence đúng giúp review đúng tốc độ thay đổi của vấn đề."
},
"8.1":{
"title":"Slide 15 mới có kết luận",
"story":"Một kỹ sư trình bày 14 slide lịch sử trước khi đến slide 15: ‘Đề xuất giữ supplier A’. Manager nói: “Lần sau hãy bắt đầu bằng câu đó.” Báo cáo sau mở đầu bằng conclusion, tiếp đến ba lý do và dữ liệu dưới mỗi lý do. Cuộc họp rút từ 40 phút xuống 15 phút.",
"memory":"Pyramid Principle tôn trọng thời gian người nghe bằng cách đưa kết luận lên trước."
},
"8.2":{
"title":"20 slide được ép thành một trang",
"story":"Team có 20 slide FACA nhưng khách hàng vẫn hỏi ‘Vậy nguyên nhân và next step là gì?’. PE thử ép mọi thứ lên một trang: Background, Current, Analysis, Action, Result, Next Step. Khi thiếu chỗ, họ buộc phải bỏ thông tin không phục vụ quyết định. Trang A3 cuối cùng rõ hơn cả deck cũ.",
"memory":"Giới hạn một trang buộc tư duy phải rõ."
},
"8.3":{
"title":"Biểu đồ đúng nhưng không ai hiểu ý",
"story":"Một slide có 6 chart, tất cả đều đúng nhưng audience không biết phải nhìn gì. Kỹ sư đổi headline từ ‘Defect trend’ thành ‘Hai action giúp defect giảm 0,7% và giữ ổn định 10 ca’. Anh giữ lại một chart duy nhất hỗ trợ câu đó. Cùng dữ liệu, câu chuyện bỗng trở nên rõ ràng.",
"memory":"Data Storytelling trả lời câu hỏi: ‘So what?’"
},
"8.4":{
"title":"Mười người, chín mươi phút, không quyết định",
"story":"Một cuộc họp claim kéo dài 90 phút. Người này kể lịch sử, người kia mở file mới, cuối cùng không ai biết ai làm gì. Tuần sau, leader gửi pre-read, ghi rõ Decision Needed và timebox 30 phút. Kết thúc cuộc họp, 4 action có owner và deadline. Không ai thấy thiếu 60 phút còn lại.",
"memory":"Meeting tốt được thiết kế quanh output, không quanh thời lượng."
},
"9.1":{
"title":"Kỹ sư giỏi nhất nhưng không lead được project",
"story":"Dũng rất sâu về một process nhưng mỗi dự án liên phòng ban anh đều gặp khó vì không hiểu Quality, Finance và Project Management. Anh vẽ chữ T cho năng lực của mình: trục dọc là process expertise, trục ngang là các skill phối hợp. Sau một năm bổ sung data, presentation và project skill, phạm vi ảnh hưởng của anh tăng rõ rệt.",
"memory":"Chiều sâu tạo chuyên môn; chiều rộng giúp chuyên môn tạo ảnh hưởng."
},
"9.2":{
"title":"Mười năm kinh nghiệm hay một năm lặp lại mười lần?",
"story":"Hai kỹ sư cùng có 10 năm làm báo cáo. Một người vẫn viết slide như cũ; người kia mỗi tuần chọn một micro-skill như headline, chart hoặc logic và xin feedback. Sau một năm, chất lượng chênh lệch rất lớn. Thâm niên giống nhau nhưng cách luyện tập khác nhau.",
"memory":"Kinh nghiệm chỉ trở thành năng lực khi có luyện tập có chủ đích và feedback."
},
"9.3":{
"title":"Lỗi cũ quay lại với người mới",
"story":"Một claim đã được xử lý năm ngoái nhưng chỉ lưu trong email của engineer cũ. Khi người đó chuyển bộ phận, lỗi tương tự lặp lại và team phải điều tra từ đầu. Sau lần này họ cập nhật FMEA, Control Plan và training material. Kiến thức từ sự cố trở thành tài sản của hệ thống thay vì ký ức cá nhân.",
"memory":"Lesson Learned chỉ có giá trị khi được đưa vào standard có thể dùng lại."
},
"9.4":{
"title":"Đến kỳ đánh giá mới cố nhớ mình đã làm gì",
"story":"Cuối năm, Linh phải viết self-review nhưng chỉ nhớ những dự án gần đây. Từ quý sau cô tạo Career Portfolio: mỗi project ghi Problem, Role, Action, Result và Learning. Đến kỳ đánh giá, cô không cần ‘kể công việc’; cô có bằng chứng impact và đường phát triển của chính mình.",
"memory":"Portfolio biến sự nghiệp từ ký ức mơ hồ thành chuỗi bằng chứng năng lực."
},
"10.1":{
"title":"Ba người cùng nghĩ người khác chịu trách nhiệm",
"story":"Một trial bị trễ vì PE nghĩ PMC đặt material, PMC nghĩ Purchasing đặt, Purchasing lại chờ PE confirm. Không ai ‘sai’ nhưng deliverable không có owner rõ. Team lập RACI: PMC Responsible, PE Manager Accountable, Purchasing Consulted. Lần trial sau không còn khoảng trống trách nhiệm.",
"memory":"RACI giải quyết khoảng trống giữa ‘có tham gia’ và ‘chịu trách nhiệm’."
},
"10.2":{
"title":"Risk score giống nhau nhưng hậu quả khác hẳn",
"story":"Hai risk đều được chấm 12. Một risk gây rework nội bộ, risk kia có thể escape tới khách hàng. Team nhận ra score chỉ là công cụ, không phải chân lý. Họ bổ sung severity rule và residual risk sau control, đồng thời quy định risk customer-critical cần escalation riêng.",
"memory":"Risk Matrix giúp ưu tiên, nhưng judgment vẫn cần hiểu bản chất hậu quả."
},
"10.3":{
"title":"Một tờ A3 thay cho cả chuỗi email",
"story":"Project có 47 email, 8 file Excel và 12 slide nhưng manager vẫn hỏi ‘Vấn đề là gì?’. Engineer gom lại thành A3: Current, Target, Root Cause, Countermeasure và Follow-up. Lần đầu tiên mọi người nhìn thấy toàn bộ logic trên cùng một trang và chốt quyết định trong 10 phút.",
"memory":"A3 là kỷ luật cô đọng tư duy, không chỉ là một form."
},
"10.4":{
"title":"Bộ nhớ ngoài đáng tin cậy",
"story":"Phúc quản lý task bằng email, sticky note, chat và trí nhớ. Anh luôn cảm giác bận vì sợ quên việc. Sau đó anh gom về bốn nơi: Goals, Projects/Actions, Calendar và Weekly Review. Số công cụ ít hơn nhưng độ tin cậy tăng lên; anh không còn kiểm tra chat liên tục chỉ để nhớ xem mình còn nợ việc gì.",
"memory":"Hệ thống cá nhân tốt giải phóng não khỏi việc nhớ cam kết để dành sức cho suy nghĩ."
},
}
