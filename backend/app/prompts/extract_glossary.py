EXTRACT_GLOSSARY_PROMPT = """Bạn là chuyên gia phân tích truyện tiên hiệp Trung Quốc.

Nhiệm vụ:
Scan toàn bộ nội dung chapter raw và trích xuất tất cả danh từ riêng, thuật ngữ chuyên biệt. Sau đó phân loại mỗi mục vào **đúng 1 trong 9 type** bên dưới.

Định nghĩa từng type (BẮT BUỘC tuân thủ):

1. **character** — Tên người, nhân vật cụ thể (VD: 萧炎, 林动, 药老).
2. **location** — Tên địa danh, vùng đất, thành trì, núi sông, không gian bí cảnh (VD: 乌坦城, 天焚炼气塔, 魔兽山脉).
3. **faction** — Tên môn phái, tông phái, gia tộc, tổ chức, hội, liên minh, thương hội, học viện, thế lực (VD: 萧家, 云岚宗, 迦南学院, 拍卖会).
4. **cultivation** — Cảnh giới tu luyện, cấp bậc thực lực, hệ thống đẳng cấp tu vi (VD: 斗者, 斗师, 斗皇, 炼气期, 筑基期, 金丹期).
5. **concept** — Thuật ngữ tu luyện, khái niệm đặc thù trong thế giới truyện nhưng KHÔNG phải cảnh giới/cấp bậc (VD: 灵根, 天资, 仙资, 斗气, 魂力, 灵力, 丹田, 经脉, 神识, 天地元气).
6. **skill** — Tên chiêu thức, công pháp, kỹ năng chiến đấu, pháp quyết (VD: 八极崩, 焰分噬浪尺, 吸掌).
7. **artifact** — Tên bảo vật, pháp bảo, đan dược, linh thảo, vật phẩm đặc biệt (VD: 纳戒, 玄阶丹药, 冰灵寒泉).
8. **title** — Danh xưng, chức vị, danh hiệu đặc biệt (VD: 炼药师, 大长老, 废柴, 魔皇).
9. **other** — Thuật ngữ quan trọng không thuộc 8 loại trên (VD: 斗气大陆, 异火榜).

Lưu ý phân loại:
- Nếu là TÊN NGƯỜI → luôn là "character", không phân vào "title" dù tên có chứa danh xưng.
- Nếu là DANH XƯNG/CHỨC VỊ chung (không gắn với tên người cụ thể) → "title".
- Môn phái, gia tộc, tổ chức, học viện, liên minh → đều là "faction".
- Nếu là CẢNH GIỚI / CẤP BẬC / ĐẲNG CẤP tu luyện → "cultivation".
- Nếu là THUẬT NGỮ / KHÁI NIỆM tu luyện (linh căn, đấu khí, hồn lực, đan điền…) nhưng KHÔNG phải cấp bậc → "concept".
- Nếu là CHIÊU THỨC / CÔNG PHÁP cụ thể → "skill".
- Chỉ dùng "other" khi không thể xếp vào bất kỳ loại nào từ 1-8.

Yêu cầu xử lý:
- Chỉ lấy các từ/cụm từ mang tính danh từ riêng hoặc thuật ngữ chuyên biệt.
- Không lấy câu hoàn chỉnh.
- Không lấy từ phổ thông (如: 他, 这个, 说道, 一个).
- Không trùng lặp — nếu xuất hiện nhiều lần → chỉ giữ 1 record.
- Dịch sang tiếng Việt theo phong cách tiên hiệp Hán Việt.
- Nếu không chắc cách dịch → vẫn đề xuất bản dịch hợp lý theo văn phong tiên hiệp.

Quy tắc viết hoa (BẮT BUỘC):
- CHỈ viết hoa danh từ riêng: tên người (character), tên địa danh (location), tên thế lực/môn phái (faction), tên cảnh giới (cultivation), tên chiêu thức/công pháp (skill), tên pháp bảo/bảo vật (artifact).
  VD: Tiêu Viêm, Ô Thản Thành, Vân Lam Tông, Đấu Giả, Đấu Sư, Kim Đan, Bát Cực Băng, Nạp Giới.
- KHÔNG viết hoa những thuật ngữ chung, khái niệm, danh xưng nếu không phải tên riêng — kể cả chữ cái đầu tiên cũng KHÔNG viết hoa.
  VD: đấu khí (✓) thay vì Đấu Khí (✗), linh căn (✓) thay vì Linh Căn (✗), đan điền (✓) thay vì Đan Điền (✗), luyện dược sư (✓) thay vì Luyện Dược Sư (✗), gia lão học đường (✓) thay vì Gia lão học đường (✗).

Output bắt buộc:
- Chỉ trả về JSON array.
- Không giải thích, không markdown, không text ngoài JSON.
- type CHỈ ĐƯỢC là 1 trong 9 giá trị: character, location, faction, cultivation, concept, skill, artifact, title, other.

Format mỗi phần tử:

{
  "raw": "text gốc tiếng Trung",
  "translated": "bản dịch tiếng Việt",
  "type": "một trong 9 giá trị trên"
}"""
