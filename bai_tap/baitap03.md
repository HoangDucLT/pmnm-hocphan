# TRAGEDY OF THE COMMONS TRONG PHẦN MỀM MÃ NGUỒN MỞ – TRƯỜNG HỢP OPENSSL

## 1. Khái niệm Tragedy of the Commons

“Tragedy of the Commons” hay “bi kịch của tài sản chung” là khái niệm mô tả tình huống một tài nguyên được nhiều người cùng sử dụng nhưng trách nhiệm duy trì tài nguyên đó lại không được phân bổ tương xứng. Mỗi cá nhân hoặc tổ chức đều có lợi ích khi khai thác tài nguyên chung, nhưng họ có xu hướng giảm phần chi phí và công sức mà mình bỏ ra để duy trì tài nguyên. Nếu tình trạng này kéo dài, tài nguyên chung có thể bị suy giảm chất lượng hoặc không còn được duy trì đầy đủ.

Trong lĩnh vực phần mềm mã nguồn mở, hiện tượng này có thể xảy ra khi một thư viện được hàng nghìn tổ chức, doanh nghiệp và dự án sử dụng nhưng chỉ có một nhóm rất nhỏ nhà phát triển chịu trách nhiệm bảo trì. Các doanh nghiệp sử dụng thư viện có thể tiết kiệm đáng kể chi phí bằng cách sử dụng phần mềm mã nguồn mở, nhưng không phải tất cả đều đóng góp nhân lực, tài chính hoặc mã nguồn trở lại cho dự án.

Linux Foundation cũng sử dụng chính khái niệm “tragedy-of-the-commons” để mô tả tình trạng người dùng hạ nguồn có thể giả định rằng các vấn đề bảo mật và bảo trì đã được người khác thực hiện và tài trợ.

## 2. Trường hợp OpenSSL trước năm 2014

OpenSSL là một thư viện mã nguồn mở quan trọng được sử dụng để cung cấp các chức năng mật mã và bảo mật cho nhiều hệ thống. Vì được sử dụng rộng rãi nên OpenSSL trở thành một phần quan trọng của hạ tầng Internet. Tuy nhiên, trước năm 2014, dự án có nguồn lực phát triển tương đối hạn chế so với mức độ quan trọng và phạm vi sử dụng của nó.

Một nghiên cứu của Linux Foundation về OpenSSL nhận định rằng trước Heartbleed, OpenSSL là ví dụ về một dự án có đội ngũ nhỏ và thời gian hạn chế cho những công việc cần thiết để đạt mức độ bảo mật cao. Điều này cho thấy sự chênh lệch giữa “giá trị mà cộng đồng nhận được” và “nguồn lực dành cho việc bảo trì”.

Một minh chứng rõ ràng xuất hiện vào tháng 4 năm 2014 với lỗ hổng được biết đến với tên Heartbleed. Theo thông báo bảo mật của OpenSSL, lỗi xuất phát từ việc thiếu kiểm tra giới hạn trong quá trình xử lý TLS heartbeat, khiến dữ liệu từ bộ nhớ của hệ thống có thể bị trả về cho đối tượng kết nối. Các phiên bản bị ảnh hưởng bao gồm OpenSSL 1.0.1a đến 1.0.1f và một số bản beta của 1.0.2.

Điều quan trọng là Heartbleed không có nghĩa OpenSSL “thất bại hoàn toàn” hay mã nguồn mở là nguyên nhân trực tiếp của lỗ hổng. Vấn đề đáng chú ý hơn là một thành phần có vai trò quan trọng đối với Internet đã không nhận được lượng nguồn lực tương xứng với mức độ phụ thuộc của các tổ chức sử dụng nó.

## 3. Vì sao OpenSSL thể hiện “bi kịch của tài sản chung”?

Trường hợp OpenSSL thể hiện khá rõ ba đặc điểm của hiện tượng này.

Thứ nhất, **có rất nhiều bên hưởng lợi**. OpenSSL được sử dụng bởi nhiều sản phẩm, máy chủ và dịch vụ khác nhau. Các tổ chức có thể tích hợp thư viện vào hệ thống của mình mà không phải tự xây dựng toàn bộ chức năng mật mã.

Thứ hai, **chi phí bảo trì tập trung vào một nhóm nhỏ**. Trong khi số lượng người sử dụng rất lớn, số người trực tiếp phát triển và xem xét mã nguồn lại nhỏ hơn nhiều. Thống kê đóng góp OpenSSL năm 2014 cho thấy một số lượng tương đối nhỏ các nhà phát triển thực hiện phần lớn commit và review của dự án.

Thứ ba, **động lực đóng góp không giống với lợi ích nhận được**. Một công ty có thể sử dụng OpenSSL để vận hành sản phẩm của mình nhưng việc tài trợ trực tiếp cho đội ngũ OpenSSL lại không nhất thiết mang lại lợi ích trước mắt rõ ràng. Vì vậy, nếu nhiều công ty đều suy nghĩ rằng “người khác sẽ tài trợ”, dự án có thể rơi vào tình trạng thiếu nguồn lực.

## 4. Hậu quả

Heartbleed cho thấy hậu quả của việc thiếu nguồn lực có thể rất lớn đối với một thư viện hạ tầng. Lỗ hổng đã tạo ra tác động rộng rãi và trở thành một trong những yếu tố thúc đẩy sự hình thành của **Core Infrastructure Initiative (CII)** vào năm 2014. Linux Foundation cho biết CII được thành lập với sự hỗ trợ của hơn 20 công ty nhằm tăng cường an toàn cho các dự án mã nguồn mở quan trọng.

Sau Heartbleed, OpenSSL cũng nhận được thêm nguồn tài trợ. Chẳng hạn, trong năm 2014, OpenSSL thông báo một khoản đóng góp khoảng 160.000 USD từ Smartisan Technology, cùng các khoản tài trợ khác, giúp dự án có thêm nhân sự làm việc toàn thời gian.

Những thay đổi này cho thấy vấn đề không chỉ nằm ở kỹ thuật mà còn nằm ở mô hình kinh tế và quản trị của phần mềm mã nguồn mở.

## 5. Đề xuất cơ chế khắc phục

Theo em, giải pháp quan trọng nhất là xây dựng một **cơ chế tài trợ bền vững dựa trên mức độ phụ thuộc của doanh nghiệp vào dự án**. Các tổ chức sử dụng thư viện quan trọng trong sản phẩm thương mại nên đóng góp tài chính định kỳ cho quỹ hoặc tổ chức quản lý dự án. Không nhất thiết mọi doanh nghiệp phải đóng góp cùng một số tiền; mức đóng góp có thể dựa trên quy mô sử dụng, doanh thu hoặc mức độ phụ thuộc vào thư viện.

Thứ hai, cần **tài trợ nhân sự bảo trì toàn thời gian**. Đối với thư viện hạ tầng quan trọng, việc chỉ dựa vào tình nguyện viên là không đủ. Một phần ngân sách nên được sử dụng để trả lương cho maintainer, reviewer và chuyên gia bảo mật. Điều này giúp dự án có người chịu trách nhiệm rõ ràng đối với việc kiểm tra mã nguồn, xử lý lỗi và phát hành bản cập nhật.

Thứ ba, cần **tăng cường kiểm thử và kiểm toán bảo mật**. Các dự án quan trọng nên được hỗ trợ về CI, kiểm thử tự động, fuzzing và kiểm toán bảo mật định kỳ. Linux Foundation cũng đề xuất các quỹ và tổ chức hỗ trợ nên tài trợ cho những hoạt động như kiểm toán, công cụ quét, CI và đội ngũ bảo mật dùng chung cho nhiều dự án.

Cuối cùng, cần xây dựng **cơ chế phối hợp giữa các doanh nghiệp sử dụng dự án**. Thay vì mỗi công ty tự xử lý vấn đề riêng, các doanh nghiệp có thể cùng tham gia một quỹ hoặc tổ chức chung để xác định những dự án quan trọng và phân bổ nguồn lực cho chúng.

## 6. Kết luận

Trường hợp OpenSSL trước năm 2014 cho thấy “tragedy of the commons” là một vấn đề thực tế trong hệ sinh thái mã nguồn mở. Một thư viện có thể được sử dụng bởi rất nhiều tổ chức nhưng vẫn phụ thuộc vào một nhóm nhỏ người bảo trì. Khi lợi ích được chia sẻ rộng rãi nhưng chi phí bảo trì không được chia sẻ tương xứng, nguy cơ thiếu nguồn lực và phát sinh vấn đề chất lượng hoặc bảo mật sẽ tăng lên.

Bài học từ OpenSSL là cộng đồng không thể chỉ xem mã nguồn mở như một tài nguyên miễn phí để sử dụng. Với những dự án đóng vai trò quan trọng đối với hạ tầng công nghệ, các tổ chức hưởng lợi cần có trách nhiệm đóng góp trở lại bằng tiền, nhân lực, kiểm thử hoặc chuyên môn. Một mô hình tài trợ ổn định kết hợp với quản trị minh bạch, kiểm thử và kiểm toán bảo mật sẽ giúp giảm nguy cơ “bi kịch của tài sản chung” và tạo điều kiện cho các dự án mã nguồn mở phát triển lâu dài.
